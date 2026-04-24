package org.cms.jpos;

import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * ISO 8583 Message Handler for CMS Platform
 * Handles various financial transaction message types
 */
public class ISOMessageHandler {
    private static final Logger logger = Logger.getLogger(ISOMessageHandler.class.getName());
    private static final Map<String, String> transactionLog = new HashMap<>();

    /**
     * Represents a simple ISO message
     */
    public static class SimpleISOMessage {
        private String mti;
        private Map<Integer, String> fields;

        public SimpleISOMessage() {
            this.fields = new HashMap<>();
        }

        public void setMTI(String mti) {
            this.mti = mti;
        }

        public String getMTI() {
            return mti;
        }

        public void set(int fieldNum, String value) {
            fields.put(fieldNum, value);
        }

        public String get(int fieldNum) {
            return fields.get(fieldNum);
        }

        public boolean hasField(int fieldNum) {
            return fields.containsKey(fieldNum);
        }

        public String getString(int fieldNum) {
            return fields.getOrDefault(fieldNum, "");
        }
    }

    /**
     * Process incoming ISO message and route to appropriate handler
     */
    public static SimpleISOMessage processMessage(SimpleISOMessage incomingMessage) {
        try {
            String mti = incomingMessage.getMTI();
            logger.info("Processing message with MTI: " + mti);

            switch (mti) {
                case "0100":
                    return handleAuthorizationRequest(incomingMessage);
                case "0200":
                    return handleBalanceInquiry(incomingMessage);
                case "0220":
                    return handleFinancialTransaction(incomingMessage);
                case "0400":
                    return handleTransactionReversal(incomingMessage);
                case "0500":
                    return handleLogoff(incomingMessage);
                case "0600":
                    return handlePINChange(incomingMessage);
                case "0800":
                    return handleEchoTest(incomingMessage);
                default:
                    logger.warning("Unknown message type: " + mti);
                    return createErrorResponse(incomingMessage, "30");
            }
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error processing message", e);
            return createErrorResponse(incomingMessage, "99");
        }
    }

    /**
     * Handle Authorization Request (0x0100 -> 0x0110)
     * Validates and approves payment transactions
     */
    private static SimpleISOMessage handleAuthorizationRequest(SimpleISOMessage request) {
        try {
            logger.info("Processing Authorization Request");
            
            SimpleISOMessage response = new SimpleISOMessage();
            response.setMTI("0110");
            
            // Copy transaction details
            if (request.hasField(2)) response.set(2, request.getString(2));
            if (request.hasField(4)) response.set(4, request.getString(4));
            if (request.hasField(11)) response.set(11, request.getString(11));
            if (request.hasField(12)) response.set(12, request.getString(12));
            if (request.hasField(13)) response.set(13, request.getString(13));
            
            // Set response code (00 = Approved)
            response.set(39, "00");
            // Set Auth Code
            response.set(38, "123456");
            
            return response;
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Authorization handler error", e);
            return createErrorResponse(request, "99");
        }
    }

    /**
     * Handle Balance Inquiry (0x0200 -> 0x0210)
     * Returns account balance
     */
    private static SimpleISOMessage handleBalanceInquiry(SimpleISOMessage request) {
        try {
            logger.info("Processing Balance Inquiry");
            
            SimpleISOMessage response = new SimpleISOMessage();
            response.setMTI("0210");
            
            // Copy transaction details
            if (request.hasField(2)) response.set(2, request.getString(2));
            if (request.hasField(11)) response.set(11, request.getString(11));
            if (request.hasField(12)) response.set(12, request.getString(12));
            if (request.hasField(13)) response.set(13, request.getString(13));
            
            // Set response code (00 = Approved)
            response.set(39, "00");
            // Set balance in field 54
            response.set(54, "840000000000001000");
            
            return response;
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Balance inquiry handler error", e);
            return createErrorResponse(request, "99");
        }
    }

    /**
     * Handle Financial Transaction (0x0220 -> 0x0230)
     * Processes withdrawal or deposit
     */
    private static SimpleISOMessage handleFinancialTransaction(SimpleISOMessage request) {
        try {
            logger.info("Processing Financial Transaction");
            
            SimpleISOMessage response = new SimpleISOMessage();
            response.setMTI("0230");
            
            // Copy transaction details
            if (request.hasField(2)) response.set(2, request.getString(2));
            if (request.hasField(4)) response.set(4, request.getString(4));
            if (request.hasField(11)) response.set(11, request.getString(11));
            if (request.hasField(12)) response.set(12, request.getString(12));
            if (request.hasField(13)) response.set(13, request.getString(13));
            
            // Set response code (00 = Approved)
            response.set(39, "00");
            // Set Auth Code
            response.set(38, "123456");
            
            return response;
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Financial transaction handler error", e);
            return createErrorResponse(request, "99");
        }
    }

    /**
     * Handle Transaction Reversal (0x0400 -> 0x0410)
     * Reverses failed or disputed transactions
     */
    private static SimpleISOMessage handleTransactionReversal(SimpleISOMessage request) {
        try {
            logger.info("Processing Transaction Reversal");
            
            SimpleISOMessage response = new SimpleISOMessage();
            response.setMTI("0410");
            
            // Copy transaction details
            if (request.hasField(2)) response.set(2, request.getString(2));
            if (request.hasField(4)) response.set(4, request.getString(4));
            if (request.hasField(37)) response.set(37, request.getString(37));
            
            // Set response code (00 = Approved)
            response.set(39, "00");
            // Set Auth Code
            response.set(38, "654321");
            
            return response;
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Reversal handler error", e);
            return createErrorResponse(request, "99");
        }
    }

    /**
     * Handle Logoff (0x0500 -> 0x0510)
     * Closes terminal session
     */
    private static SimpleISOMessage handleLogoff(SimpleISOMessage request) {
        try {
            logger.info("Processing Logoff");
            
            SimpleISOMessage response = new SimpleISOMessage();
            response.setMTI("0510");
            
            // Copy transaction details
            if (request.hasField(11)) response.set(11, request.getString(11));
            if (request.hasField(12)) response.set(12, request.getString(12));
            
            // Set response code (00 = Approved)
            response.set(39, "00");
            
            return response;
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Logoff handler error", e);
            return createErrorResponse(request, "99");
        }
    }

    /**
     * Handle PIN Change (0x0600 -> 0x0610)
     * Updates customer PIN
     */
    private static SimpleISOMessage handlePINChange(SimpleISOMessage request) {
        try {
            logger.info("Processing PIN Change");
            
            SimpleISOMessage response = new SimpleISOMessage();
            response.setMTI("0610");
            
            // Copy transaction details
            if (request.hasField(2)) response.set(2, request.getString(2));
            if (request.hasField(11)) response.set(11, request.getString(11));
            if (request.hasField(12)) response.set(12, request.getString(12));
            
            // Set response code (00 = Approved)
            response.set(39, "00");
            
            return response;
        } catch (Exception e) {
            logger.log(Level.SEVERE, "PIN change handler error", e);
            return createErrorResponse(request, "99");
        }
    }

    /**
     * Handle Echo Test (0x0800 -> 0x0810)
     * Network connectivity verification
     */
    private static SimpleISOMessage handleEchoTest(SimpleISOMessage request) {
        try {
            logger.info("Processing Echo Test");
            
            SimpleISOMessage response = new SimpleISOMessage();
            response.setMTI("0810");
            
            // Copy transaction details
            if (request.hasField(11)) response.set(11, request.getString(11));
            if (request.hasField(12)) response.set(12, request.getString(12));
            
            // Set response code (00 = Approved)
            response.set(39, "00");
            
            return response;
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Echo test handler error", e);
            return createErrorResponse(request, "99");
        }
    }

    /**
     * Create error response message
     */
    private static SimpleISOMessage createErrorResponse(SimpleISOMessage request, String responseCode) {
        SimpleISOMessage response = new SimpleISOMessage();
        String mti = request.getMTI();
        String responseMTI = mti.substring(0, 1) + "1" + mti.substring(2);
        response.setMTI(responseMTI);
        response.set(39, responseCode);
        return response;
    }

    /**
     * Process raw ISO 8583 message bytes
     * Parses, processes, and returns serialized response
     */
    public static byte[] processRawMessage(byte[] rawMessage, int length) {
        try {
            if (length < 17) {
                logger.warning("Message too short: " + length + " bytes");
                return null;
            }

            // Parse message length (first 2 bytes, big-endian)
            int msgLen = ((rawMessage[0] & 0xFF) << 8) | (rawMessage[1] & 0xFF);
            if (msgLen > length - 2) {
                logger.warning("Invalid message length: " + msgLen);
                return null;
            }

            // Extract message (skip length prefix)
            byte[] message = new byte[msgLen];
            System.arraycopy(rawMessage, 2, message, 0, msgLen);

            // Skip TPDU (5 bytes)
            int pos = 5;

            // Parse MTI (4 bytes)
            String mti = new String(message, pos, 4);
            pos += 4;

            // Parse bitmap (8 bytes = 64 fields)
            long bitmap = 0;
            for (int i = 0; i < 8; i++) {
                bitmap = (bitmap << 8) | (message[pos + i] & 0xFF);
            }
            pos += 8;

            logger.info("Parsing message MTI=" + mti + " bitmap=" + Long.toHexString(bitmap));

            // Create message object
            SimpleISOMessage requestMsg = new SimpleISOMessage();
            requestMsg.setMTI(mti);

            // Parse fields based on bitmap
            for (int fieldNum = 2; fieldNum <= 64; fieldNum++) {
                if ((bitmap & (1L << (64 - fieldNum))) != 0) {
                    String fieldValue = parseField(message, pos, fieldNum);
                    if (fieldValue != null) {
                        requestMsg.set(fieldNum, fieldValue);
                        // Update position for variable-length fields
                        pos = updateFieldPosition(message, pos, fieldNum);
                    } else {
                        break;
                    }
                }
            }

            // Process the message
            SimpleISOMessage responseMsg = processMessage(requestMsg);

            // Serialize response
            return serializeMessage(responseMsg);

        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error processing raw message", e);
            return null;
        }
    }

    /**
     * Parse a single field from message bytes
     */
    private static String parseField(byte[] message, int startPos, int fieldNum) {
        try {
            // Simplified field parsing - handles basic fixed-length fields
            switch (fieldNum) {
                case 2:  // PAN (LLVAR, up to 19 digits)
                    int panLen = Integer.parseInt(new String(message, startPos, 2));
                    return new String(message, startPos + 2, panLen);

                case 3:  // Processing Code (6 chars)
                    return new String(message, startPos, 6);
                case 4:  // Amount (12 chars)
                    return new String(message, startPos, 12);
                case 7:  // MMDDHHMMSS (10 chars)
                    return new String(message, startPos, 10);
                case 11: // STAN (6 chars)
                    return new String(message, startPos, 6);
                case 12: // HHMMSS (6 chars)
                    return new String(message, startPos, 6);
                case 13: // MMDD (4 chars)
                    return new String(message, startPos, 4);
                case 22: // POS Entry Mode (3 chars)
                    return new String(message, startPos, 3);
                case 25: // Function Code (2 chars)
                    return new String(message, startPos, 2);
                case 35: // Track 2 (LLVAR)
                    int t2Len = Integer.parseInt(new String(message, startPos, 2));
                    return new String(message, startPos + 2, t2Len);
                case 37: // RRN (12 chars)
                    return new String(message, startPos, 12);
                case 39: // Response Code (2 chars)
                    return new String(message, startPos, 2);
                case 41: // Terminal ID (8 chars)
                    return new String(message, startPos, 8);
                case 42: // Merchant ID (15 chars)
                    return new String(message, startPos, 15);
                case 49: // Currency Code (3 chars)
                    return new String(message, startPos, 3);
                case 52: // PIN Block (8 bytes)
                    return toHex(message, startPos, 8);
                case 55: // EMV Data (LLLVAR)
                    int emvLen = Integer.parseInt(new String(message, startPos, 3));
                    return toHex(message, startPos + 3, emvLen);
                default:
                    logger.fine("Skipping field " + fieldNum);
                    return null;
            }
        } catch (Exception e) {
            logger.log(Level.WARNING, "Error parsing field " + fieldNum, e);
            return null;
        }
    }

    /**
     * Update position after parsing field
     */
    private static int updateFieldPosition(byte[] message, int startPos, int fieldNum) {
        try {
            switch (fieldNum) {
                case 2:  // LLVAR
                    int panLen = Integer.parseInt(new String(message, startPos, 2));
                    return startPos + 2 + panLen;
                case 35: // LLVAR
                    int t2Len = Integer.parseInt(new String(message, startPos, 2));
                    return startPos + 2 + t2Len;
                case 55: // LLLVAR
                    int emvLen = Integer.parseInt(new String(message, startPos, 3));
                    return startPos + 3 + emvLen;
                default:
                    // Fixed-length fields
                    return getFieldLength(fieldNum) + startPos;
            }
        } catch (Exception e) {
            logger.log(Level.WARNING, "Error updating field position for field " + fieldNum, e);
            return startPos;
        }
    }

    /**
     * Get field length
     */
    private static int getFieldLength(int fieldNum) {
        switch (fieldNum) {
            case 3:  return 6;
            case 4:  return 12;
            case 7:  return 10;
            case 11: return 6;
            case 12: return 6;
            case 13: return 4;
            case 22: return 3;
            case 25: return 2;
            case 37: return 12;
            case 39: return 2;
            case 41: return 8;
            case 42: return 15;
            case 49: return 3;
            case 52: return 8;
            default: return 0;
        }
    }

    /**
     * Convert bytes to hex string
     */
    private static String toHex(byte[] data, int offset, int length) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < length && offset + i < data.length; i++) {
            sb.append(String.format("%02X", data[offset + i]));
        }
        return sb.toString();
    }

    /**
     * Serialize SimpleISOMessage to bytes
     */
    private static byte[] serializeMessage(SimpleISOMessage msg) {
        try {
            byte[] mtiBytes = msg.getMTI().getBytes();
            
            // Build bitmap
            long bitmap = 0;
            for (int i = 2; i <= 64; i++) {
                if (msg.hasField(i)) {
                    bitmap |= (1L << (64 - i));
                }
            }
            
            // Start building message
            java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
            
            // Write TPDU
            baos.write(new byte[]{0x60, 0x00, 0x00, 0x00, 0x00});
            
            // Write MTI
            baos.write(mtiBytes);
            
            // Write bitmap (8 bytes, big-endian)
            baos.write((byte)((bitmap >> 56) & 0xFF));
            baos.write((byte)((bitmap >> 48) & 0xFF));
            baos.write((byte)((bitmap >> 40) & 0xFF));
            baos.write((byte)((bitmap >> 32) & 0xFF));
            baos.write((byte)((bitmap >> 24) & 0xFF));
            baos.write((byte)((bitmap >> 16) & 0xFF));
            baos.write((byte)((bitmap >> 8) & 0xFF));
            baos.write((byte)(bitmap & 0xFF));
            
            // Write fields
            for (int fieldNum = 2; fieldNum <= 64; fieldNum++) {
                if (msg.hasField(fieldNum)) {
                    String value = msg.getString(fieldNum);
                    serializeField(baos, fieldNum, value);
                }
            }
            
            byte[] messageBytes = baos.toByteArray();
            
            // Prepend message length (2 bytes, big-endian)
            byte[] result = new byte[messageBytes.length + 2];
            result[0] = (byte)((messageBytes.length >> 8) & 0xFF);
            result[1] = (byte)(messageBytes.length & 0xFF);
            System.arraycopy(messageBytes, 0, result, 2, messageBytes.length);
            
            return result;
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error serializing message", e);
            return null;
        }
    }

    /**
     * Serialize a single field
     */
    private static void serializeField(java.io.ByteArrayOutputStream baos, int fieldNum, String value) throws Exception {
        switch (fieldNum) {
            case 2:  // PAN (LLVAR)
                baos.write(String.format("%02d", value.length()).getBytes());
                baos.write(value.getBytes());
                break;
            case 3:  // Processing Code (FIXED 6)
                baos.write(String.format("%-6s", value).replace(' ', '0').getBytes());
                break;
            case 4:  // Amount (FIXED 12)
                baos.write(String.format("%012d", Long.parseLong(value)).getBytes());
                break;
            case 7:  // MMDDHHMMSS (FIXED 10)
                baos.write(String.format("%-10s", value).getBytes());
                break;
            case 11: // STAN (FIXED 6)
                baos.write(String.format("%06d", Integer.parseInt(value)).getBytes());
                break;
            case 12: // HHMMSS (FIXED 6)
                baos.write(String.format("%-6s", value).getBytes());
                break;
            case 13: // MMDD (FIXED 4)
                baos.write(String.format("%-4s", value).getBytes());
                break;
            case 22: // POS Entry Mode (FIXED 3)
                baos.write(String.format("%-3s", value).getBytes());
                break;
            case 25: // Function Code (FIXED 2)
                baos.write(String.format("%-2s", value).getBytes());
                break;
            case 35: // Track 2 (LLVAR)
                baos.write(String.format("%02d", value.length()).getBytes());
                baos.write(value.getBytes());
                break;
            case 37: // RRN (FIXED 12)
                baos.write(String.format("%012d", Long.parseLong(value)).getBytes());
                break;
            case 38: // Auth Code (FIXED 6)
                baos.write(String.format("%-6s", value).getBytes());
                break;
            case 39: // Response Code (FIXED 2)
                baos.write(String.format("%02d", Integer.parseInt(value)).getBytes());
                break;
            case 41: // Terminal ID (FIXED 8)
                baos.write(String.format("%-8s", value).getBytes());
                break;
            case 42: // Merchant ID (FIXED 15)
                baos.write(String.format("%-15s", value).getBytes());
                break;
            case 49: // Currency Code (FIXED 3)
                baos.write(String.format("%03d", Integer.parseInt(value)).getBytes());
                break;
            case 52: // PIN Block (BINARY 8)
                baos.write(fromHex(value));
                break;
            case 54: // Balance (LLVAR)
                baos.write(String.format("%02d", value.length()).getBytes());
                baos.write(value.getBytes());
                break;
            case 55: // EMV Data (LLLVAR)
                baos.write(String.format("%03d", value.length() / 2).getBytes());
                baos.write(fromHex(value));
                break;
            default:
                logger.fine("Skipping field " + fieldNum + " during serialization");
        }
    }

    /**
     * Convert hex string to bytes
     */
    private static byte[] fromHex(String hex) {
        byte[] result = new byte[hex.length() / 2];
        for (int i = 0; i < result.length; i++) {
            result[i] = (byte)Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return result;
    }

    /**
     * Get transaction log
     */
    public static Map<String, String> getTransactionLog() {
        return transactionLog;
    }

    /**
     * Clear transaction log
     */
    public static void clearTransactionLog() {
        transactionLog.clear();
    }
}

