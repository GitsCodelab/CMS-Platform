package org.cms.jpos;

import org.jpos.iso.ISOException;
import org.jpos.iso.ISOMsg;
import org.jpos.iso.packager.GenericPackager;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

public class ISOMessageHandler {
    private static final Logger logger = Logger.getLogger(ISOMessageHandler.class.getName());
    private static final AppConfig CONFIG = AppConfig.load();
    private static final byte[] VARIANT_RIGHT_HALF = hexToBytes("C0C0C0C000000000");
    private static final Map<String, Set<Integer>> REQUIRED_FIELDS = buildRequiredFields();
    private static final Map<String, Set<Integer>> ALLOWED_FIELDS = buildAllowedFields();
    private static final Map<String, Long> REPLAY_CACHE = new ConcurrentHashMap<>();

    public static byte[] processRawMessage(byte[] message, int length) {
        long now = System.currentTimeMillis();
        cleanupReplayCache(now);

        RequestContext context = new RequestContext();
        try {
            byte[] isoBytes = validateEnvelope(message, length);
            GenericPackager packager = loadPackager();
            ISOMsg request = unpack(packager, isoBytes);

            context.mti = safeGet(request, 0);
            context.stan = safeGet(request, 11);
            context.terminalId = safeGet(request, 41);

            validateRequest(request, now);
            logISO("request", request);

            ISOMsg response = buildResponse(request, packager);
            if (request.hasField(64)) {
                response.set(64, calculateMACBytes(response, CONFIG.macKeys.get(0)));
            }

            logISO("response", response);
            return buildFinalResponse(response.pack());
        } catch (RequestValidationException e) {
            logger.warning(String.format(
                "request_rejected code=%s reason=%s mti=%s stan=%s terminal=%s",
                e.responseCode,
                e.getMessage(),
                nullToDash(context.mti),
                nullToDash(context.stan),
                nullToDash(context.terminalId)
            ));
            return buildError(context.mti, e.responseCode);
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Processing error", e);
            return buildError(context.mti, "96");
        }
    }

    private static byte[] validateEnvelope(byte[] message, int length) throws RequestValidationException {
        if (message == null || length != message.length) {
            throw new RequestValidationException("30", "Message length mismatch");
        }
        if (length <= 5 || length > CONFIG.maxMessageLength) {
            throw new RequestValidationException("30", "Invalid message envelope length");
        }
        return Arrays.copyOfRange(message, 5, length);
    }

    private static GenericPackager loadPackager() {
        InputStream is = ISOMessageHandler.class.getClassLoader().getResourceAsStream("iso87.xml");
        if (is == null) {
            throw new IllegalStateException("iso87.xml not found in resources");
        }
        try {
            return new GenericPackager(is);
        } catch (ISOException e) {
            throw new IllegalStateException("Unable to load ISO packager", e);
        }
    }

    private static ISOMsg unpack(GenericPackager packager, byte[] isoBytes) throws ISOException {
        ISOMsg iso = new ISOMsg();
        iso.setPackager(packager);
        iso.unpack(isoBytes);
        return iso;
    }

    private static void validateRequest(ISOMsg iso, long now) throws Exception {
        String mti = iso.getMTI();
        Set<Integer> required = REQUIRED_FIELDS.get(mti);
        Set<Integer> allowed = ALLOWED_FIELDS.get(mti);

        if (required == null || allowed == null) {
            throw new RequestValidationException("30", "Unsupported MTI: " + mti);
        }

        Set<Integer> present = getPresentFields(iso);
        for (Integer field : present) {
            if (!allowed.contains(field)) {
                throw new RequestValidationException("30", "Unexpected field " + field);
            }
        }

        for (Integer field : required) {
            if (!iso.hasField(field)) {
                throw new RequestValidationException("30", "Missing required field " + field);
            }
        }

        if (CONFIG.requireMac && !iso.hasField(64)) {
            throw new RequestValidationException("30", "MAC is required");
        }

        validateFieldFormats(iso);
        validateReplay(iso, now);

        if (iso.hasField(64) && !validateMAC(iso)) {
            throw new RequestValidationException("96", "MAC validation failed");
        }

        if (iso.hasField(52) && !validateDUKPT(iso)) {
            throw new RequestValidationException("55", "DUKPT validation failed");
        }
    }

    private static void validateFieldFormats(ISOMsg iso) throws RequestValidationException, ISOException {
        if (iso.hasField(2)) {
            validateDigits(iso.getString(2), 12, 19, "2");
            if (!passesLuhn(iso.getString(2))) {
                throw new RequestValidationException("30", "PAN failed Luhn validation");
            }
        }

        if (iso.hasField(3)) validateDigitsExact(iso.getString(3), 6, "3");
        if (iso.hasField(4)) validateDigitsExact(iso.getString(4), 12, "4");
        if (iso.hasField(7)) validateDigitsExact(iso.getString(7), 10, "7");
        if (iso.hasField(11)) validateDigitsExact(iso.getString(11), 6, "11");
        if (iso.hasField(12)) validateDigitsExact(iso.getString(12), 6, "12");
        if (iso.hasField(13)) validateDigitsExact(iso.getString(13), 4, "13");
        if (iso.hasField(22)) validateDigitsExact(iso.getString(22), 3, "22");
        if (iso.hasField(25)) validateDigitsExact(iso.getString(25), 2, "25");
        if (iso.hasField(49)) validateDigitsExact(iso.getString(49), 3, "49");
        if (iso.hasField(70)) validateDigitsExact(iso.getString(70), 3, "70");

        if (iso.hasField(41)) validatePrintableExact(iso.getString(41), 8, "41");
        if (iso.hasField(42)) validatePrintableMax(iso.getString(42), 15, "42");

        if (iso.hasField(35)) {
            String track2 = iso.getString(35);
            if (track2.length() > 37 || !track2.matches("[0-9=]+")) {
                throw new RequestValidationException("30", "Invalid field 35");
            }
        }

        if (iso.hasField(62)) {
            String ksn = iso.getString(62).trim();
            if (!ksn.matches("[0-9A-F]{20}")) {
                throw new RequestValidationException("30", "Invalid KSN format");
            }
            validateKsnCounter(ksn);
        }
    }

    private static void validateReplay(ISOMsg iso, long now) throws ISOException, RequestValidationException {
        String replayKey = String.join(
            "|",
            iso.getMTI(),
            safeGet(iso, 11),
            safeGet(iso, 41),
            safeGet(iso, 62)
        );

        Long previous = REPLAY_CACHE.putIfAbsent(replayKey, now);
        if (previous != null) {
            throw new RequestValidationException("94", "Replay detected");
        }
    }

    private static boolean validateMAC(ISOMsg iso) {
        try {
            byte[] actual = iso.getBytes(64);
            for (byte[] key : CONFIG.macKeys) {
                byte[] expected = calculateMACBytes(iso, key);
                if (MessageDigest.isEqual(expected, actual)) {
                    return true;
                }
            }
            return false;
        } catch (Exception e) {
            logger.log(Level.WARNING, "MAC validation failed", e);
            return false;
        }
    }

    private static boolean validateDUKPT(ISOMsg iso) {
        try {
            String pan = iso.getString(2);
            String ksnHex = iso.getString(62).trim();
            byte[] ksn = hexToBytes(ksnHex);
            byte[] encryptedPinBlock = iso.getBytes(52);
            byte[] panBlock = buildPanBlock(pan);

            for (byte[] bdk : CONFIG.bdkKeys) {
                byte[] pinKey = derivePinKey(bdk, ksn);
                byte[] clearPinBlock = decryptTripleDes(pinKey, encryptedPinBlock);
                byte[] pinBlock = xor(clearPinBlock, panBlock);
                if (isValidIso0PinBlock(pinBlock)) {
                    return true;
                }
            }
            return false;
        } catch (Exception e) {
            logger.log(Level.WARNING, "DUKPT validation failed", e);
            return false;
        }
    }

    private static ISOMsg buildResponse(ISOMsg request, GenericPackager packager) throws ISOException {
        String requestMti = request.getMTI();
        String responseMti;
        switch (requestMti) {
            case "0200":
                responseMti = "0210";
                break;
            case "0100":
                responseMti = "0110";
                break;
            case "0400":
                responseMti = "0410";
                break;
            case "0800":
                responseMti = "0810";
                break;
            default:
                throw new ISOException("Unsupported MTI: " + requestMti);
        }

        ISOMsg response = new ISOMsg();
        response.setPackager(packager);
        response.setMTI(responseMti);

        copyIfPresent(request, response, 2, 3, 4, 7, 11, 12, 13, 22, 25, 41, 42, 49);

        if ("0200".equals(requestMti)) {
            response.set(39, "00");
            response.set(54, "840000000000001000");
        } else if ("0100".equals(requestMti)) {
            response.set(39, "00");
            response.set(38, "123456");
        } else if ("0400".equals(requestMti)) {
            response.set(39, "00");
        } else if ("0800".equals(requestMti)) {
            copyIfPresent(request, response, 70);
            response.set(39, "00");
        }

        response.unset(35, 52, 62, 64);
        return response;
    }

    private static void copyIfPresent(ISOMsg source, ISOMsg target, int... fields) throws ISOException {
        for (int field : fields) {
            if (source.hasField(field)) {
                Object value = source.getValue(field);
                if (value instanceof byte[]) {
                    target.set(field, (byte[]) value);
                } else {
                    target.set(field, source.getString(field));
                }
            }
        }
    }

    private static byte[] buildError(String requestMti, String code) {
        try {
            GenericPackager packager = loadPackager();
            ISOMsg error = new ISOMsg();
            error.setPackager(packager);
            error.setMTI(toResponseMTI(requestMti));
            error.set(39, code);
            return buildFinalResponse(error.pack());
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Unable to build error response", e);
            return null;
        }
    }

    private static String toResponseMTI(String requestMti) {
        if (requestMti == null || requestMti.length() != 4) {
            return "0210";
        }
        return requestMti.substring(0, 2) + "10";
    }

    private static byte[] buildFinalResponse(byte[] isoData) {
        byte[] tpdu = new byte[]{0x60, 0x00, 0x00, 0x00, 0x00};
        byte[] full = new byte[tpdu.length + isoData.length];
        System.arraycopy(tpdu, 0, full, 0, tpdu.length);
        System.arraycopy(isoData, 0, full, tpdu.length, isoData.length);
        return full;
    }

    private static void logISO(String type, ISOMsg iso) {
        try {
            List<String> parts = new ArrayList<>();
            parts.add("event=" + type);
            parts.add("mti=" + iso.getMTI());
            parts.add("stan=" + maskField(11, safeGet(iso, 11)));
            parts.add("terminal=" + maskField(41, safeGet(iso, 41)));

            List<Integer> present = new ArrayList<>(getPresentFields(iso));
            Collections.sort(present);
            for (Integer field : present) {
                parts.add("f" + field + "=" + maskField(field, safeGet(iso, field)));
            }

            logger.info(String.join(" ", parts));
        } catch (Exception e) {
            logger.warning("Logging failed");
        }
    }

    private static String maskField(int field, String value) {
        if (value == null) {
            return "-";
        }
        switch (field) {
            case 2:
                return maskPan(value);
            case 35:
                int idx = value.indexOf('=');
                String pan = idx >= 0 ? value.substring(0, idx) : value;
                String suffix = idx >= 0 ? value.substring(idx) : "";
                return maskPan(pan) + suffix;
            case 52:
            case 62:
            case 64:
                return "<redacted>";
            default:
                return value.trim();
        }
    }

    private static String maskPan(String pan) {
        if (pan == null || pan.length() < 10) {
            return "<masked>";
        }
        return pan.substring(0, 6) + "******" + pan.substring(pan.length() - 4);
    }

    private static byte[] calculateMACBytes(ISOMsg iso, byte[] key) throws Exception {
        ISOMsg macMsg = (ISOMsg) iso.clone();
        macMsg.setPackager(iso.getPackager());
        macMsg.set(64, new byte[8]);
        return retailMacAnsiX919(key, macMsg.pack());
    }

    private static byte[] retailMacAnsiX919(byte[] key, byte[] data) throws Exception {
        byte[] left = Arrays.copyOfRange(key, 0, 8);
        byte[] right = Arrays.copyOfRange(key, 8, 16);
        byte[] padded = zeroPad(data, 8);
        byte[] state = new byte[8];

        for (int i = 0; i < padded.length; i += 8) {
            byte[] block = Arrays.copyOfRange(padded, i, i + 8);
            state = encryptDes(left, xor(state, block));
        }

        state = decryptDes(right, state);
        return encryptDes(left, state);
    }

    private static byte[] derivePinKey(byte[] bdk, byte[] ksn) throws Exception {
        String ksnHex = bytesToHex(ksn);
        String paddedKsnHex = String.format("%20s", ksnHex).replace(' ', 'F');
        byte[] initialKsn = Arrays.copyOfRange(hexToBytes(paddedKsnHex), 0, 8);
        initialKsn[7] &= (byte) 0xE0;

        byte[] leftBdk = Arrays.copyOfRange(bdk, 0, 8);
        byte[] rightBdk = Arrays.copyOfRange(bdk, 8, 16);

        byte[] currentKey = concat(
            encryptTripleDesEde(bdk, initialKsn),
            encryptTripleDesEde(
                concat(xor(leftBdk, VARIANT_RIGHT_HALF), xor(rightBdk, VARIANT_RIGHT_HALF)),
                initialKsn
            )
        );

        byte[] ksnBytes = Arrays.copyOfRange(hexToBytes(ksnHex.substring(ksnHex.length() - 16)), 0, 8);
        ksnBytes[4] &= (byte) 0xE0;

        byte[] transactionCounter = Arrays.copyOfRange(ksn, 7, 10);
        transactionCounter[0] &= 0x1F;
        byte[] shiftReg = hexToBytes("100000");

        byte[] left = new byte[8];
        byte[] right = new byte[8];

        while (notZero(shiftReg)) {
            byte[] masked = andBytes(shiftReg, transactionCounter);
            if (notZero(masked)) {
                System.arraycopy(currentKey, 0, left, 0, 8);
                System.arraycopy(currentKey, 8, right, 0, 8);

                orInto(ksnBytes, shiftReg, 5);

                byte[] cryptoReg1 = xor(ksnBytes, right);
                cryptoReg1 = encryptDes(left, cryptoReg1);
                cryptoReg1 = xor(cryptoReg1, right);

                byte[] leftVariant = xor(left, VARIANT_RIGHT_HALF);
                byte[] rightVariant = xor(right, VARIANT_RIGHT_HALF);

                byte[] cryptoReg2 = xor(ksnBytes, rightVariant);
                cryptoReg2 = encryptDes(leftVariant, cryptoReg2);
                cryptoReg2 = xor(cryptoReg2, rightVariant);

                currentKey = concat(cryptoReg2, cryptoReg1);
            }
            shiftRight(shiftReg);
        }

        currentKey[7] ^= (byte) 0xFF;
        currentKey[15] ^= (byte) 0xFF;
        return currentKey;
    }

    private static byte[] buildPanBlock(String pan) {
        String pan12 = pan.substring(pan.length() - 13, pan.length() - 1);
        return hexToBytes("0000" + pan12);
    }

    private static boolean isValidIso0PinBlock(byte[] pinBlock) {
        String hex = bytesToHex(pinBlock);
        if (hex.length() != 16 || hex.charAt(0) != '0') {
            return false;
        }

        int pinLength = Character.digit(hex.charAt(1), 16);
        if (pinLength < 4 || pinLength > 12) {
            return false;
        }

        for (int i = 2; i < 2 + pinLength; i++) {
            if (!Character.isDigit(hex.charAt(i))) {
                return false;
            }
        }

        for (int i = 2 + pinLength; i < hex.length(); i++) {
            if (hex.charAt(i) != 'F') {
                return false;
            }
        }

        return true;
    }

    private static void validateKsnCounter(String ksnHex) throws RequestValidationException {
        byte[] ksn = hexToBytes(ksnHex);
        int counter = ((ksn[7] & 0x1F) << 16) | ((ksn[8] & 0xFF) << 8) | (ksn[9] & 0xFF);
        if (counter <= 0) {
            throw new RequestValidationException("30", "KSN counter must be greater than zero");
        }
        if (Integer.bitCount(counter) > 10) {
            throw new RequestValidationException("30", "KSN counter exceeds allowed bit population");
        }
    }

    private static void validateDigitsExact(String value, int length, String field) throws RequestValidationException {
        if (value == null || value.length() != length || !value.matches("\\d+")) {
            throw new RequestValidationException("30", "Invalid numeric field " + field);
        }
    }

    private static void validateDigits(String value, int minLength, int maxLength, String field) throws RequestValidationException {
        if (value == null || value.length() < minLength || value.length() > maxLength || !value.matches("\\d+")) {
            throw new RequestValidationException("30", "Invalid numeric field " + field);
        }
    }

    private static void validatePrintableExact(String value, int length, String field) throws RequestValidationException {
        if (value == null || value.length() != length || !value.matches("[ -~]+")) {
            throw new RequestValidationException("30", "Invalid printable field " + field);
        }
    }

    private static void validatePrintableMax(String value, int maxLength, String field) throws RequestValidationException {
        if (value == null || value.length() > maxLength || !value.matches("[ -~]+")) {
            throw new RequestValidationException("30", "Invalid printable field " + field);
        }
    }

    private static boolean passesLuhn(String pan) {
        int sum = 0;
        boolean doubleDigit = false;
        for (int i = pan.length() - 1; i >= 0; i--) {
            int digit = pan.charAt(i) - '0';
            if (doubleDigit) {
                digit *= 2;
                if (digit > 9) {
                    digit -= 9;
                }
            }
            sum += digit;
            doubleDigit = !doubleDigit;
        }
        return sum % 10 == 0;
    }

    private static Set<Integer> getPresentFields(ISOMsg iso) throws ISOException {
        Set<Integer> present = new HashSet<>();
        for (int i = 2; i <= iso.getMaxField(); i++) {
            if (iso.hasField(i)) {
                present.add(i);
            }
        }
        return present;
    }

    private static void cleanupReplayCache(long now) {
        long maxAgeMs = CONFIG.replayWindowSeconds * 1000L;
        REPLAY_CACHE.entrySet().removeIf(entry -> (now - entry.getValue()) > maxAgeMs);
    }

    private static byte[] encryptDes(byte[] key, byte[] data) throws Exception {
        Cipher cipher = Cipher.getInstance("DES/ECB/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "DES"));
        return cipher.doFinal(data);
    }

    private static byte[] decryptDes(byte[] key, byte[] data) throws Exception {
        Cipher cipher = Cipher.getInstance("DES/ECB/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key, "DES"));
        return cipher.doFinal(data);
    }

    private static byte[] decryptTripleDes(byte[] key, byte[] data) throws Exception {
        Cipher cipher = Cipher.getInstance("DESede/ECB/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(expandKey(key), "DESede"));
        return cipher.doFinal(data);
    }

    private static byte[] encryptTripleDesEde(byte[] key, byte[] data) throws Exception {
        byte[] left = Arrays.copyOfRange(key, 0, 8);
        byte[] right = Arrays.copyOfRange(key, 8, 16);
        return encryptDes(left, decryptDes(right, encryptDes(left, data)));
    }

    private static byte[] expandKey(byte[] key16) {
        byte[] out = new byte[24];
        System.arraycopy(key16, 0, out, 0, 16);
        System.arraycopy(key16, 0, out, 16, 8);
        return out;
    }

    private static byte[] xor(byte[] left, byte[] right) {
        byte[] out = new byte[left.length];
        for (int i = 0; i < left.length; i++) {
            out[i] = (byte) (left[i] ^ right[i]);
        }
        return out;
    }

    private static byte[] andBytes(byte[] left, byte[] right) {
        byte[] out = new byte[left.length];
        for (int i = 0; i < left.length; i++) {
            out[i] = (byte) (left[i] & right[i]);
        }
        return out;
    }

    private static void orInto(byte[] target, byte[] source, int offset) {
        for (int i = 0; i < source.length; i++) {
            target[offset + i] |= source[i];
        }
    }

    private static void shiftRight(byte[] value) {
        int carry = 0;
        for (int i = 0; i < value.length; i++) {
            int newCarry = value[i] & 0x01;
            value[i] = (byte) (((value[i] & 0xFF) >> 1) | (carry << 7));
            carry = newCarry;
        }
    }

    private static boolean notZero(byte[] value) {
        for (byte b : value) {
            if (b != 0x00) {
                return true;
            }
        }
        return false;
    }

    private static byte[] concat(byte[] left, byte[] right) {
        byte[] out = new byte[left.length + right.length];
        System.arraycopy(left, 0, out, 0, left.length);
        System.arraycopy(right, 0, out, left.length, right.length);
        return out;
    }

    private static byte[] zeroPad(byte[] data, int blockSize) {
        int remainder = data.length % blockSize;
        if (remainder == 0) {
            return data;
        }
        return Arrays.copyOf(data, data.length + (blockSize - remainder));
    }

    private static byte[] hexToBytes(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }

    private static String bytesToHex(byte[] data) {
        StringBuilder sb = new StringBuilder();
        for (byte b : data) {
            sb.append(String.format("%02X", b));
        }
        return sb.toString();
    }

    private static String safeGet(ISOMsg iso, int field) {
        try {
            if (field == 0) {
                return iso.getMTI();
            }
            return iso.hasField(field) ? iso.getString(field) : null;
        } catch (Exception e) {
            return null;
        }
    }

    private static String nullToDash(String value) {
        return value == null ? "-" : value;
    }

    private static Map<String, Set<Integer>> buildRequiredFields() {
        Map<String, Set<Integer>> map = new HashMap<>();
        map.put("0200", setOf(2, 3, 4, 7, 11, 12, 13, 22, 25, 41, 42, 49, 52, 62, 64));
        map.put("0100", setOf(2, 3, 4, 7, 11, 12, 13, 22, 25, 41, 42, 49, 64));
        map.put("0400", setOf(2, 3, 4, 7, 11, 12, 13, 41, 42, 49, 64));
        map.put("0800", setOf(7, 11, 70, 64));
        return Collections.unmodifiableMap(map);
    }

    private static Map<String, Set<Integer>> buildAllowedFields() {
        Map<String, Set<Integer>> map = new HashMap<>();
        map.put("0200", setOf(2, 3, 4, 7, 11, 12, 13, 22, 25, 35, 41, 42, 49, 52, 62, 64));
        map.put("0100", setOf(2, 3, 4, 7, 11, 12, 13, 22, 25, 41, 42, 49, 64));
        map.put("0400", setOf(2, 3, 4, 7, 11, 12, 13, 41, 42, 49, 64));
        map.put("0800", setOf(7, 11, 70, 64));
        return Collections.unmodifiableMap(map);
    }

    private static Set<Integer> setOf(int... values) {
        Set<Integer> set = new HashSet<>();
        for (int value : values) {
            set.add(value);
        }
        return Collections.unmodifiableSet(set);
    }

    private static final class RequestContext {
        private String mti;
        private String stan;
        private String terminalId;
    }

    private static final class RequestValidationException extends Exception {
        private final String responseCode;

        private RequestValidationException(String responseCode, String message) {
            super(message);
            this.responseCode = responseCode;
        }
    }
}
