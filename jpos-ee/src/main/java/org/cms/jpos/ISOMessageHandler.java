package org.cms.jpos;

import org.jpos.iso.*;
import org.jpos.iso.packager.GenericPackager;

import java.io.InputStream;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class ISOMessageHandler {

    private static final Logger logger = Logger.getLogger(ISOMessageHandler.class.getName());
    private static final byte[] BDK = hexToBytes("0123456789ABCDEFFEDCBA9876543210");
    private static final byte[] VARIANT_RIGHT_HALF = hexToBytes("C0C0C0C000000000");
    private static final byte[] MAC_KEY = hexToBytes("0123456789ABCDEFFEDCBA9876543210");

    public static byte[] processRawMessage(byte[] message, int length) {
        try {

            // ================= DEBUG =================
            System.out.println("RAW HEX: " + bytesToHex(message));

            // Gateway already removed the 2-byte TCP length header.
            // At this point the message starts with the 5-byte TPDU.
            byte[] isoBytes = Arrays.copyOfRange(message, 5, length);

            // ================= PACKAGER =================
            InputStream is = ISOMessageHandler.class
                    .getClassLoader()
                    .getResourceAsStream("iso87.xml");

            if (is == null) {
                throw new RuntimeException("iso87.xml not found in resources");
            }

            GenericPackager packager = new GenericPackager(is);

            // ================= UNPACK =================
            ISOMsg iso = new ISOMsg();
            iso.setPackager(packager);
            iso.unpack(isoBytes);

            logISO("REQUEST", iso);

            // ================= VALIDATION =================
            if (iso.hasField(64)) {
                if (!validateMAC(iso)) {
                    return buildError(packager, "0210", "96");
                }
            }

            if (iso.hasField(52)) {
                if (!validateDUKPT(iso)) {
                    return buildError(packager, "0210", "55");
                }
            }

            // ================= BUSINESS =================
            ISOMsg resp = buildResponse(iso);

            // ================= MAC =================
            if (iso.hasField(64)) {
                String mac = calculateMAC(resp);
                resp.set(64, hexToBytes(mac));
            }

            logISO("RESPONSE", resp);

            // ================= PACK =================
            byte[] respISO = resp.pack();

            // ================= FINAL RESPONSE =================
            return buildFinalResponse(respISO);

        } catch (Exception e) {
            logger.log(Level.SEVERE, "Processing error", e);
            return null;
        }
    }

    // ================= RESPONSE =================
    private static ISOMsg buildResponse(ISOMsg req) throws ISOException {

        ISOMsg resp = (ISOMsg) req.clone();

        switch (req.getMTI()) {
            case "0200":
                resp.setMTI("0210");
                resp.set(39, "00");
                resp.set(54, "840000000000001000");
                break;

            case "0100":
                resp.setMTI("0110");
                resp.set(39, "00");
                resp.set(38, "123456");
                break;

            case "0400":
                resp.setMTI("0410");
                resp.set(39, "00");
                break;

            case "0800":
                resp.setMTI("0810");
                resp.set(39, "00");
                break;

            default:
                resp.setMTI("0210");
                resp.set(39, "30");
        }

        return resp;
    }

    // ================= ERROR =================
    private static byte[] buildError(GenericPackager packager, String mti, String code) throws Exception {
        ISOMsg err = new ISOMsg();
        err.setPackager(packager);
        err.setMTI(mti);
        err.set(39, code);

        byte[] iso = err.pack();
        return buildFinalResponse(iso);
    }

    // ================= FINAL RESPONSE =================
    private static byte[] buildFinalResponse(byte[] isoData) {

        // TPDU
        byte[] tpdu = new byte[]{0x60, 0x00, 0x00, 0x00, 0x00};

        // Combine TPDU + ISO
        byte[] full = new byte[tpdu.length + isoData.length];
        System.arraycopy(tpdu, 0, full, 0, tpdu.length);
        System.arraycopy(isoData, 0, full, tpdu.length, isoData.length);
        return full;
    }

    // ================= LOG =================
    private static void logISO(String type, ISOMsg iso) {
        try {
            logger.info("\n====== " + type + " ISO ======");
            logger.info("MTI: " + iso.getMTI());

            for (int i = 2; i <= iso.getMaxField(); i++) {
                if (iso.hasField(i)) {
                    logger.info("F" + i + ": " + iso.getString(i));
                }
            }

        } catch (Exception e) {
            logger.warning("Logging failed");
        }
    }

    // ================= MAC =================
    private static boolean validateMAC(ISOMsg iso) {
        try {
            if (!iso.hasField(64)) {
                return false;
            }
            byte[] expected = calculateMACBytes(iso);
            byte[] actual = iso.getBytes(64);
            return MessageDigest.isEqual(expected, actual);
        } catch (Exception e) {
            logger.log(Level.WARNING, "MAC validation failed", e);
            return false;
        }
    }

    private static String calculateMAC(ISOMsg iso) {
        try {
            return bytesToHex(calculateMACBytes(iso));
        } catch (Exception e) {
            throw new RuntimeException("MAC calculation failed", e);
        }
    }

    // ================= DUKPT =================
    private static boolean validateDUKPT(ISOMsg iso) {
        try {
            if (!iso.hasField(52) || !iso.hasField(62) || !iso.hasField(2)) {
                return false;
            }

            byte[] ksn = hexToBytes(iso.getString(62).trim());
            if (ksn.length != 10) {
                return false;
            }

            byte[] pinKey = derivePinKey(BDK, ksn);
            byte[] encryptedPinBlock = iso.getBytes(52);
            byte[] clearPinBlock = decryptTripleDes(pinKey, encryptedPinBlock);
            byte[] panBlock = buildPanBlock(iso.getString(2));
            byte[] pinBlock = xor(clearPinBlock, panBlock);

            return isValidIso0PinBlock(pinBlock);
        } catch (Exception e) {
            logger.log(Level.WARNING, "DUKPT validation failed", e);
            return false;
        }
    }

    // ================= UTILS =================
    private static byte[] calculateMACBytes(ISOMsg iso) throws Exception {
        ISOMsg macMsg = (ISOMsg) iso.clone();
        macMsg.setPackager(iso.getPackager());
        macMsg.set(64, new byte[8]);
        return retailMac(MAC_KEY, macMsg.pack());
    }

    private static byte[] retailMac(byte[] key, byte[] data) throws Exception {
        byte[] left = Arrays.copyOfRange(key, 0, 8);
        byte[] right = Arrays.copyOfRange(key, 8, 16);
        byte[] padded = padRightZero(data, 8);
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

        for (int i = 2 + pinLength; i < hex.length(); i++) {
            if (hex.charAt(i) != 'F') {
                return false;
            }
        }

        for (int i = 2; i < 2 + pinLength; i++) {
            if (!Character.isDigit(hex.charAt(i))) {
                return false;
            }
        }

        return true;
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

    private static byte[] encryptTripleDes(byte[] key, byte[] data) throws Exception {
        Cipher cipher = Cipher.getInstance("DESede/ECB/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(expandKey(key), "DESede"));
        return cipher.doFinal(data);
    }

    private static byte[] encryptTripleDesEde(byte[] key, byte[] data) throws Exception {
        byte[] left = Arrays.copyOfRange(key, 0, 8);
        byte[] right = Arrays.copyOfRange(key, 8, 16);
        return encryptDes(left, decryptDes(right, encryptDes(left, data)));
    }

    private static byte[] decryptTripleDes(byte[] key, byte[] data) throws Exception {
        Cipher cipher = Cipher.getInstance("DESede/ECB/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(expandKey(key), "DESede"));
        return cipher.doFinal(data);
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

    private static byte[] padRightZero(byte[] data, int blockSize) {
        int rem = data.length % blockSize;
        if (rem == 0) {
            return data;
        }
        return Arrays.copyOf(data, data.length + (blockSize - rem));
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
}
