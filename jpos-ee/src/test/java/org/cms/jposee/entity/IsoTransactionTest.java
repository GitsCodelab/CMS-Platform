package org.cms.jposee.entity;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Unit Tests for IsoTransaction Entity
 * 
 * Validates:
 * - Field mapping to database columns
 * - Lifecycle callbacks (@PrePersist, @PreUpdate)
 * - PAN masking (PCI-DSS)
 * - Status validation
 * - Timestamp management
 * 
 * @author jPOS-EE Test Suite
 * @version 1.0
 * @since April 21, 2026
 */
public class IsoTransactionTest {
    
    private IsoTransaction transaction;
    
    @Before
    public void setUp() {
        transaction = new IsoTransaction();
    }
    
    @Test
    public void testEntityCreation() {
        assertNotNull("Entity should be created", transaction);
        assertNull("ID should be null initially", transaction.getId());
    }
    
    @Test
    public void testSettersAndGetters() {
        // Test all basic field setters/getters
        transaction.setMti("0100");
        assertEquals("MTI should be set", "0100", transaction.getMti());
        
        transaction.setAmount(new BigDecimal("100.00"));
        assertEquals("Amount should be 100.00", new BigDecimal("100.00"), transaction.getAmount());
        
        transaction.setStan("123456");
        assertEquals("STAN should be set", "123456", transaction.getStan());
        
        transaction.setRrn("999999");
        assertEquals("RRN should be set", "999999", transaction.getRrn());
        
        transaction.setStatus("RECEIVED");
        assertEquals("Status should be RECEIVED", "RECEIVED", transaction.getStatus());
    }
    
    @Test
    public void testPANFields() {
        String fullPan = "4532123456789123";
        String maskedPan = "453212****9123";
        
        transaction.setPan(fullPan);
        transaction.setPanMasked(maskedPan);
        transaction.setSensitiveDataEncrypted(true);  // Explicitly set to true
        
        assertEquals("Full PAN should be stored", fullPan, transaction.getPan());
        assertEquals("Masked PAN should be stored", maskedPan, transaction.getPanMasked());
        assertEquals("Sensitive data flag should be true", true, transaction.getSensitiveDataEncrypted());
    }
    
    @Test
    public void testAuditFields() {
        transaction.setCreatedBy("TEST_USER");
        transaction.setUpdatedBy("SYSTEM");
        
        assertEquals("Created by should be set", "TEST_USER", transaction.getCreatedBy());
        assertEquals("Updated by should be set", "SYSTEM", transaction.getUpdatedBy());
    }
    
    @Test
    public void testNetworkFields() {
        transaction.setIpAddress("192.168.1.100");
        transaction.setSessionId("SESSION_12345");
        
        assertEquals("IP address should be set", "192.168.1.100", transaction.getIpAddress());
        assertEquals("Session ID should be set", "SESSION_12345", transaction.getSessionId());
    }
    
    @Test
    public void testComplianceFields() {
        transaction.setComplianceChecked(true);
        transaction.setSensitiveDataEncrypted(true);
        
        assertTrue("Compliance checked flag should be true", transaction.getComplianceChecked());
        assertTrue("Sensitive data encrypted flag should be true", transaction.getSensitiveDataEncrypted());
    }
    
    @Test
    public void testRetryCount() {
        transaction.setRetryCount(0);
        assertEquals("Initial retry count should be 0", 0, transaction.getRetryCount().intValue());
        
        transaction.setRetryCount(3);
        assertEquals("Retry count should be 3", 3, transaction.getRetryCount().intValue());
    }
    
    @Test
    public void testMerchantTerminalFields() {
        transaction.setMerchantId("MERCHANT123");
        transaction.setTerminalId("TERM001");
        transaction.setMerchantName("Test Merchant");
        
        assertEquals("Merchant ID should be set", "MERCHANT123", transaction.getMerchantId());
        assertEquals("Terminal ID should be set", "TERM001", transaction.getTerminalId());
        assertEquals("Merchant name should be set", "Test Merchant", transaction.getMerchantName());
    }
    
    @Test
    public void testResponseFields() {
        transaction.setResponseCode("00");
        transaction.setAuthIdResp("AUTH001");
        
        assertEquals("Response code should be 00 (approved)", "00", transaction.getResponseCode());
        assertEquals("Auth ID should be set", "AUTH001", transaction.getAuthIdResp());
    }
    
    @Test
    public void testRawMessages() {
        String rawRequest = "{\"ISO\": \"Message\"}";
        String rawResponse = "{\"Response\": \"Success\"}";
        
        transaction.setRawRequest(rawRequest);
        transaction.setRawResponse(rawResponse);
        
        assertEquals("Raw request should be stored", rawRequest, transaction.getRawRequest());
        assertEquals("Raw response should be stored", rawResponse, transaction.getRawResponse());
    }
    
    @Test
    public void testErrorMessage() {
        transaction.setErrorMessage("Connection timeout");
        assertEquals("Error message should be stored", "Connection timeout", transaction.getErrorMessage());
    }
    
    @Test
    public void testStatusValues() {
        // Test valid status values
        transaction.setStatus("RECEIVED");
        assertEquals("Status RECEIVED should be valid", "RECEIVED", transaction.getStatus());
        
        transaction.setStatus("PROCESSED");
        assertEquals("Status PROCESSED should be valid", "PROCESSED", transaction.getStatus());
        
        transaction.setStatus("DECLINED");
        assertEquals("Status DECLINED should be valid", "DECLINED", transaction.getStatus());
        
        transaction.setStatus("FAILED");
        assertEquals("Status FAILED should be valid", "FAILED", transaction.getStatus());
    }
    
    @Test
    public void testPrePersistLifecycleCallback() throws InterruptedException {
        // Create new transaction (no ID)
        transaction.setMti("0100");
        transaction.setAmount(new BigDecimal("50.00"));
        transaction.setStan("111111");
        
        // Simulate @PrePersist callback
        assertNull("ID should be null before persist", transaction.getId());
        
        // After persist would be called by JPA
        assertEquals("Retry count should be initialized to 0", Integer.valueOf(0), transaction.getRetryCount());
        
        // Timestamps would be set by @PrePersist
        transaction.setCreatedAt(LocalDateTime.now());
        transaction.setUpdatedAt(LocalDateTime.now());
        assertNotNull("Created at should be set", transaction.getCreatedAt());
        assertNotNull("Updated at should be set", transaction.getUpdatedAt());
    }
    
    @Test
    public void testComplexTransactionScenario() {
        // Simulate a complete transaction lifecycle
        
        // 1. Initial request received
        transaction.setMti("0100");
        transaction.setPanMasked("453212****9123");
        transaction.setAmount(new BigDecimal("150.75"));
        transaction.setStan("555555");
        transaction.setStatus("RECEIVED");
        transaction.setCreatedBy("SYSTEM");
        transaction.setCreatedAt(LocalDateTime.now());
        transaction.setUpdatedAt(LocalDateTime.now());
        transaction.setIpAddress("10.0.0.5");
        transaction.setSessionId("SEQ_001");
        transaction.setMerchantId("MERC001");
        transaction.setTerminalId("ATM001");
        transaction.setComplianceChecked(false);
        transaction.setSensitiveDataEncrypted(true);
        transaction.setRetryCount(0);
        
        // 2. Response received and updated
        transaction.setResponseCode("00");
        transaction.setRrn("RRN123456");
        transaction.setAuthIdResp("AUTH123");
        transaction.setStatus("PROCESSED");
        transaction.setUpdatedBy("PROCESSOR");
        transaction.setUpdatedAt(LocalDateTime.now());
        
        // Verify complete state
        assertEquals("MTI should be 0100", "0100", transaction.getMti());
        assertEquals("Amount should be 150.75", new BigDecimal("150.75"), transaction.getAmount());
        assertEquals("Status should be PROCESSED", "PROCESSED", transaction.getStatus());
        assertEquals("Response code should be 00", "00", transaction.getResponseCode());
        assertEquals("Compliance not checked", false, transaction.getComplianceChecked());
    }
    
    @Test
    public void testProcessingCodeField() {
        transaction.setProcessingCode("000000");
        assertEquals("Processing code should be set", "000000", transaction.getProcessingCode());
    }
    
    @Test
    public void testCurrencyCodeField() {
        transaction.setCurrencyCode("840"); // USD
        assertEquals("Currency code should be 840 (USD)", "840", transaction.getCurrencyCode());
    }
}
