package org.cms.jposee.util;

import org.junit.Test;
import static org.junit.Assert.*;

import java.math.BigDecimal;

/**
 * Unit Tests for IsoUtil Utility Class
 * 
 * Validates:
 * - PAN masking (PCI-DSS Requirement 3.2.1)
 * - Amount extraction and validation
 * - STAN validation
 * - RRN handling
 * - Response code parsing
 * - Field validation
 * 
 * @author jPOS-EE Test Suite
 * @version 1.0
 * @since April 21, 2026
 */
public class IsoUtilTest {
    
    // ============================================================
    // PAN MASKING TESTS (PCI-DSS Requirement 3.2.1)
    // ============================================================
    
    @Test
    public void testMaskPANSuccess() {
        String fullPan = "4532123456789123";
        String maskedPan = IsoUtil.maskPAN(fullPan);
        
        assertEquals("Masked PAN format incorrect", "453212****9123", maskedPan);
    }
    
    @Test
    public void testMaskPANWithDifferentLengths() {
        // Test 13-digit PAN
        String pan13 = "4532123456789";
        String masked13 = IsoUtil.maskPAN(pan13);
        assertEquals("13-digit PAN masked incorrectly", "453212****6789", masked13);
        
        // Test 19-digit PAN
        String pan19 = "4532123456789123456";
        String masked19 = IsoUtil.maskPAN(pan19);
        assertEquals("19-digit PAN masked incorrectly", "453212****3456", masked19);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testMaskPANWithInvalidFormat() {
        IsoUtil.maskPAN("453212ABC789123"); // Contains letters
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testMaskPANTooShort() {
        IsoUtil.maskPAN("123456"); // Less than 13 digits
    }
    
    @Test
    public void testMaskPANWithNull() {
        assertNull("Null PAN should return null", IsoUtil.maskPAN(null));
    }
    
    @Test
    public void testIsMaskedTrue() {
        String maskedPan = "453212****9123";
        assertTrue("Should detect masked PAN", IsoUtil.isMasked(maskedPan));
    }
    
    @Test
    public void testIsMaskedFalse() {
        String fullPan = "4532123456789123";
        assertFalse("Should not detect unmasked PAN", IsoUtil.isMasked(fullPan));
    }
    
    // ============================================================
    // AMOUNT EXTRACTION TESTS
    // ============================================================
    
    @Test
    public void testExtractAmountSuccess() {
        // 10000 cents = $100.00
        BigDecimal amount = IsoUtil.extractAmount("10000");
        assertEquals("Amount should be $100.00", new BigDecimal("100"), amount);
    }
    
    @Test
    public void testExtractAmountWithCents() {
        // 15075 cents = $150.75
        BigDecimal amount = IsoUtil.extractAmount("15075");
        assertEquals("Amount should be $150.75", new BigDecimal("150.75"), amount);
    }
    
    @Test
    public void testExtractAmountZero() {
        BigDecimal amount = IsoUtil.extractAmount("0");
        assertEquals("Zero cents should be $0.00", new BigDecimal("0"), amount);
    }
    
    @Test
    public void testExtractAmountNull() {
        BigDecimal amount = IsoUtil.extractAmount(null);
        assertEquals("Null amount should return $0.00", BigDecimal.ZERO, amount);
    }
    
    @Test(expected = NumberFormatException.class)
    public void testExtractAmountInvalid() {
        IsoUtil.extractAmount("ABC123"); // Non-numeric
    }
    
    @Test
    public void testIsValidAmount() {
        BigDecimal maxAmount = new BigDecimal("1000.00");
        
        assertTrue("Amount $50 should be valid", 
                   IsoUtil.isValidAmount(new BigDecimal("50.00"), maxAmount));
        
        assertTrue("Amount $1000 (max) should be valid", 
                   IsoUtil.isValidAmount(new BigDecimal("1000.00"), maxAmount));
        
        assertFalse("Amount $1001 should be invalid (exceeds max)", 
                    IsoUtil.isValidAmount(new BigDecimal("1001.00"), maxAmount));
        
        assertFalse("Amount $0 should be invalid (must be > 0)", 
                    IsoUtil.isValidAmount(BigDecimal.ZERO, maxAmount));
    }
    
    // ============================================================
    // STAN EXTRACTION TESTS
    // ============================================================
    
    @Test
    public void testExtractSTANSuccess() {
        String stan = IsoUtil.extractSTAN("000000123456");
        assertEquals("STAN should be 123456", "123456", stan);
    }
    
    @Test
    public void testExtractSTANWithoutLeadingZeros() {
        String stan = IsoUtil.extractSTAN("123456");
        assertEquals("STAN should remain 123456", "123456", stan);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testExtractSTANNull() {
        IsoUtil.extractSTAN(null);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testExtractSTANEmpty() {
        IsoUtil.extractSTAN("");
    }
    
    // ============================================================
    // RRN EXTRACTION TESTS
    // ============================================================
    
    @Test
    public void testExtractRRNSuccess() {
        String rrn = IsoUtil.extractRRN("RRN12345678A");  // Exactly 12 chars
        assertEquals("RRN should be exactly 12 chars", "RRN12345678A", rrn);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testExtractRRNTooShort() {
        IsoUtil.extractRRN("RRN12345"); // Only 8 chars
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testExtractRRNTooLong() {
        IsoUtil.extractRRN("RRN123456789ABC"); // 15 chars
    }
    
    // ============================================================
    // RESPONSE CODE PARSING TESTS
    // ============================================================
    
    @Test
    public void testParseResponseCodeSuccess() {
        String code = IsoUtil.parseResponseCode("00");
        assertEquals("Response code should be 00", "00", code);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testParseResponseCodeInvalidFormat() {
        IsoUtil.parseResponseCode("000"); // 3 digits instead of 2
    }
    
    @Test
    public void testGetStatusFromResponseCodeApproved() {
        String status = IsoUtil.getStatusFromResponseCode("00");
        assertEquals("Code 00 should return PROCESSED", "PROCESSED", status);
    }
    
    @Test
    public void testGetStatusFromResponseCodeDeclined() {
        String status = IsoUtil.getStatusFromResponseCode("05");
        assertEquals("Code 05 should return DECLINED", "DECLINED", status);
    }
    
    @Test
    public void testGetStatusFromResponseCodeError() {
        String status = IsoUtil.getStatusFromResponseCode("99");
        assertEquals("Code 99 should return FAILED", "FAILED", status);
    }
    
    // ============================================================
    // AUTH ID EXTRACTION TESTS
    // ============================================================
    
    @Test
    public void testExtractAuthIdSuccess() {
        String authId = IsoUtil.extractAuthId("AUTH01");
        assertEquals("Auth ID should be extracted", "AUTH01", authId);
    }
    
    @Test
    public void testExtractAuthIdNull() {
        assertNull("Null auth ID should return null", IsoUtil.extractAuthId(null));
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testExtractAuthIdTooLong() {
        IsoUtil.extractAuthId("TOOLONG123"); // Longer than 6 chars
    }
    
    // ============================================================
    // MTI EXTRACTION TESTS
    // ============================================================
    
    @Test
    public void testExtractMTISuccess() {
        String mti = IsoUtil.extractMTI("0100");
        assertEquals("MTI should be 0100", "0100", mti);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void testExtractMTIInvalidFormat() {
        IsoUtil.extractMTI("01A0"); // Contains letter
    }
    
    @Test
    public void testGetMTIDescriptionKnown() {
        String desc = IsoUtil.getMTIDescription("0100");
        assertEquals("MTI 0100 should be Authorization Request", 
                     "Authorization Request", desc);
    }
    
    @Test
    public void testGetMTIDescriptionMultipleTypes() {
        assertEquals("0110 should be Authorization Response", 
                     "Authorization Response", IsoUtil.getMTIDescription("0110"));
        
        assertEquals("0200 should be Refund Request", 
                     "Refund Request", IsoUtil.getMTIDescription("0200"));
        
        assertEquals("0400 should be Reversal Request", 
                     "Reversal Request", IsoUtil.getMTIDescription("0400"));
    }
    
    // ============================================================
    // FIELD VALIDATION TESTS
    // ============================================================
    
    @Test
    public void testIsValidMerchantId() {
        assertTrue("5-digit merchant ID should be valid", 
                   IsoUtil.isValidMerchantId("12345"));
        
        assertTrue("15-digit merchant ID should be valid", 
                   IsoUtil.isValidMerchantId("123456789012345"));
        
        assertFalse("4-digit merchant ID too short", 
                    IsoUtil.isValidMerchantId("1234"));
        
        assertFalse("16-digit merchant ID too long", 
                    IsoUtil.isValidMerchantId("1234567890123456"));
        
        assertFalse("Null merchant ID invalid", 
                    IsoUtil.isValidMerchantId(null));
    }
    
    @Test
    public void testIsValidTerminalId() {
        assertTrue("Single-char terminal ID should be valid", 
                   IsoUtil.isValidTerminalId("A"));
        
        assertTrue("8-char terminal ID should be valid", 
                   IsoUtil.isValidTerminalId("ATM00001"));
        
        assertFalse("9-char terminal ID too long", 
                    IsoUtil.isValidTerminalId("ATM000001"));
        
        assertFalse("Null terminal ID invalid", 
                    IsoUtil.isValidTerminalId(null));
    }
    
    // ============================================================
    // INTEGRATION SCENARIOS
    // ============================================================
    
    @Test
    public void testCompleteTransactionFieldExtraction() {
        // Simulate extracting all fields from a transaction
        
        String pan = "4532123456789123";
        String maskedPan = IsoUtil.maskPAN(pan);
        String amount = "15075";
        BigDecimal amountDecimal = IsoUtil.extractAmount(amount);
        String stan = "000000123456";
        String extractedStan = IsoUtil.extractSTAN(stan);
        String responseCode = "00";
        String status = IsoUtil.getStatusFromResponseCode(responseCode);
        
        assertEquals("PAN masked correctly", "453212****9123", maskedPan);
        assertEquals("Amount converted correctly", new BigDecimal("150.75"), amountDecimal);
        assertEquals("STAN extracted correctly", "123456", extractedStan);
        assertEquals("Status from code correct", "PROCESSED", status);
    }
}
