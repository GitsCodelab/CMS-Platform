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
