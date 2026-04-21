package org.cms.jposee.util;

import java.math.BigDecimal;
import java.util.regex.Pattern;

/**
 * Utility class for ISO 8583 field extraction and PCI-compliance operations
 * Provides safe field parsing and PAN masking for transaction processing
 * 
 * @author jPOS-EE Persistence Layer
 * @version 1.0
 * @since April 21, 2026
 */
public class IsoUtil {
    
    private static final Pattern PAN_PATTERN = Pattern.compile("^\\d{13,19}$");
    private static final Pattern AMOUNT_PATTERN = Pattern.compile("^\\d+$");
    
    // ============================================================
    // PAN MASKING (PCI-DSS Requirement 3.2.1)
    // ============================================================
    
    /**
     * Mask PAN (Primary Account Number) for secure logging
     * Shows only first 6 and last 4 digits
     * Example: 4532123456789123 -> 453212****9123
     * 
     * @param pan the full PAN (13-19 digits)
     * @return masked PAN showing only first 6 and last 4 digits
     * @throws IllegalArgumentException if PAN is invalid
     */
    public static String maskPAN(String pan) {
        if (pan == null || pan.isEmpty()) {
            return null;
        }
        
        if (!PAN_PATTERN.matcher(pan).matches()) {
            throw new IllegalArgumentException("Invalid PAN format. Must be 13-19 digits");
        }
        
        // Minimum PAN length is 13 (not 10 as was checking before)
        if (pan.length() < 13) {
            throw new IllegalArgumentException("PAN too short. Must be at least 13 digits");
        }
        
        String first6 = pan.substring(0, 6);
        String last4 = pan.substring(pan.length() - 4);
        return first6 + "****" + last4;
    }
    
    /**
     * Check if PAN is already masked
     * 
     * @param pan the PAN to check
     * @return true if PAN appears to be masked (contains ****)
     */
    public static boolean isMasked(String pan) {
        return pan != null && pan.contains("****");
    }
    
    // ============================================================
    // AMOUNT EXTRACTION & VALIDATION
    // ============================================================
    
    /**
     * Extract amount from ISO field (typically field 4)
     * ISO amounts are in cents (divide by 100 for dollars)
     * 
     * @param amountInCents the amount in cents as string
     * @return BigDecimal amount in dollars
     * @throws NumberFormatException if amount is invalid
     */
    public static BigDecimal extractAmount(String amountInCents) {
        if (amountInCents == null || amountInCents.isEmpty()) {
            return BigDecimal.ZERO;
        }
        
        if (!AMOUNT_PATTERN.matcher(amountInCents).matches()) {
            throw new NumberFormatException("Invalid amount format: " + amountInCents);
        }
        
        long cents = Long.parseLong(amountInCents);
        return new BigDecimal(cents).divide(new BigDecimal(100));
    }
    
    /**
     * Validate amount is within acceptable range
     * 
     * @param amount the transaction amount in dollars
     * @param maxAmount maximum allowed amount
     * @return true if amount is valid
     */
    public static boolean isValidAmount(BigDecimal amount, BigDecimal maxAmount) {
        return amount != null 
            && amount.compareTo(BigDecimal.ZERO) > 0 
            && amount.compareTo(maxAmount) <= 0;
    }
    
    // ============================================================
    // STAN EXTRACTION & VALIDATION
    // ============================================================
    
    /**
     * Extract STAN (System Trace Audit Number) from ISO message
     * STAN is 12 digits, used to uniquely identify a transaction within a day
     * 
     * @param stan the STAN from ISO field
     * @return the STAN string (12 digits)
     * @throws IllegalArgumentException if STAN is invalid
     */
    public static String extractSTAN(String stan) {
        if (stan == null || stan.isEmpty()) {
            throw new IllegalArgumentException("STAN cannot be empty");
        }
        
        // Remove leading zeros for storage, but keep as string
        String trimmed = stan.replaceAll("^0+", "");
        if (trimmed.isEmpty()) {
            trimmed = "0";
        }
        
        if (!Pattern.matches("^\\d{1,12}$", trimmed)) {
            throw new IllegalArgumentException("Invalid STAN format: " + stan);
        }
        
        return trimmed;
    }
    
    // ============================================================
    // RRN EXTRACTION & VALIDATION
    // ============================================================
    
    /**
     * Extract RRN (Retrieval Reference Number) from response
     * RRN is 12 characters, provided by the processor/acquirer
     * 
     * @param rrn the RRN from ISO response
     * @return the RRN string (12 chars)
     * @throws IllegalArgumentException if RRN is invalid
     */
    public static String extractRRN(String rrn) {
        if (rrn == null || rrn.isEmpty()) {
            throw new IllegalArgumentException("RRN cannot be empty");
        }
        
        if (rrn.length() != 12) {
            throw new IllegalArgumentException("RRN must be 12 characters: " + rrn);
        }
        
        return rrn;
    }
    
    // ============================================================
    // RESPONSE CODE HANDLING
    // ============================================================
    
    /**
     * Parse response code from ISO response
     * Codes: 00=approved, 05=declined, 10-99=errors
     * 
     * @param responseCode the 2-digit response code
     * @return the response code string
     * @throws IllegalArgumentException if code is invalid
     */
    public static String parseResponseCode(String responseCode) {
        if (responseCode == null || responseCode.isEmpty()) {
            throw new IllegalArgumentException("Response code cannot be empty");
        }
        
        if (!Pattern.matches("^\\d{2}$", responseCode)) {
            throw new IllegalArgumentException("Response code must be 2 digits: " + responseCode);
        }
        
        return responseCode;
    }
    
    /**
     * Determine transaction status from response code
     * 
     * @param responseCode the 2-digit response code
     * @return status string: PROCESSED, FAILED, DECLINED
     */
    public static String getStatusFromResponseCode(String responseCode) {
        if ("00".equals(responseCode)) {
            return "PROCESSED";
        } else if ("05".equals(responseCode)) {
            return "DECLINED";
        } else {
            return "FAILED";
        }
    }
    
    // ============================================================
    // AUTH ID EXTRACTION
    // ============================================================
    
    /**
     * Extract Authorization ID from response
     * Typically 6 alphanumeric characters
     * 
     * @param authId the auth ID from response
     * @return the auth ID (trimmed)
     */
    public static String extractAuthId(String authId) {
        if (authId == null || authId.isEmpty()) {
            return null;
        }
        
        String trimmed = authId.trim();
        if (trimmed.length() > 6) {
            throw new IllegalArgumentException("Auth ID too long: " + trimmed);
        }
        
        return trimmed;
    }
    
    // ============================================================
    // MTI EXTRACTION & VALIDATION
    // ============================================================
    
    /**
     * Extract and validate MTI (Message Type Indicator)
     * MTI is 4 digits indicating message type and class
     * 0100=Authorization, 0200=Reversal, 0400=Refund, etc.
     * 
     * @param mti the MTI from ISO message
     * @return the MTI string (4 digits)
     * @throws IllegalArgumentException if MTI is invalid
     */
    public static String extractMTI(String mti) {
        if (mti == null || mti.isEmpty()) {
            throw new IllegalArgumentException("MTI cannot be empty");
        }
        
        if (!Pattern.matches("^[0-9]{4}$", mti)) {
            throw new IllegalArgumentException("Invalid MTI format (must be 4 digits): " + mti);
        }
        
        return mti;
    }
    
    /**
     * Get human-readable description of MTI
     * 
     * @param mti the 4-digit MTI
     * @return description like "Authorization Request"
     */
    public static String getMTIDescription(String mti) {
        switch (mti) {
            case "0100": return "Authorization Request";
            case "0110": return "Authorization Response";
            case "0120": return "Authorization Reversal";
            case "0200": return "Refund Request";
            case "0210": return "Refund Response";
            case "0400": return "Reversal Request";
            case "0410": return "Reversal Response";
            case "0420": return "Reversal Notification";
            case "0800": return "Network Management";
            case "0810": return "Network Management Response";
            default: return "Unknown MTI: " + mti;
        }
    }
    
    // ============================================================
    // FIELD LENGTH VALIDATION
    // ============================================================
    
    /**
     * Validate merchant ID format
     * 
     * @param merchantId the merchant ID
     * @return true if valid
     */
    public static boolean isValidMerchantId(String merchantId) {
        return merchantId != null 
            && merchantId.length() >= 5 
            && merchantId.length() <= 15;
    }
    
    /**
     * Validate terminal ID format
     * 
     * @param terminalId the terminal ID
     * @return true if valid
     */
    public static boolean isValidTerminalId(String terminalId) {
        return terminalId != null 
            && terminalId.length() >= 1 
            && terminalId.length() <= 8;
    }
}
