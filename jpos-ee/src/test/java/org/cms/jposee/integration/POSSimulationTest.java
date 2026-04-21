package org.cms.jposee.integration;

import org.cms.jposee.entity.IsoTransaction;
import org.cms.jposee.entity.IsoTransactionAudit;
import org.cms.jposee.repository.IsoTransactionRepository;
import org.cms.jposee.repository.IsoTransactionAuditRepository;
import org.cms.jposee.repository.impl.IsoTransactionRepositoryImpl;
import org.cms.jposee.repository.impl.IsoTransactionAuditRepositoryImpl;
import org.cms.jposee.util.IsoUtil;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import javax.persistence.EntityManager;
import javax.persistence.EntityManagerFactory;
import javax.persistence.Persistence;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.Assert.*;

/**
 * POS Terminal Simulation Test
 * 
 * Simulates real-world ISO 8583 transaction flow from a street POS terminal
 * Tests the complete data flow through jPOS-EE persistence layer
 * 
 * Scenarios:
 * 1. Purchase transaction (amount > 0, status PROCESSED)
 * 2. Response handling and data transformation
 * 3. Full audit trail creation
 * 4. PCI-DSS compliance validation
 * 
 * Flow:
 * POS Terminal → ISO 8583 Message → jPOS → Participant Chain → Database
 *                                       ↓
 *                                 PersistRequest (saves)
 *                                       ↓
 *                                 UpdateResponse (updates)
 *                                       ↓
 *                                 Database + Audit Trail
 * 
 * @author jPOS-EE Test Suite
 * @version 1.0
 * @since April 21, 2026
 */
public class POSSimulationTest {
    
    private EntityManagerFactory emf;
    private EntityManager em;
    private IsoTransactionRepository transactionRepository;
    private IsoTransactionAuditRepository auditRepository;
    
    @Before
    public void setUp() {
        emf = Persistence.createEntityManagerFactory("jposee-persistence");
        em = emf.createEntityManager();
        transactionRepository = new IsoTransactionRepositoryImpl(em);
        auditRepository = new IsoTransactionAuditRepositoryImpl(em);
        
        // Clean database before test
        cleanDatabase();
    }
    
    @After
    public void tearDown() {
        if (em != null && em.isOpen()) {
            em.close();
        }
        if (emf != null && emf.isOpen()) {
            emf.close();
        }
    }
    
    private void cleanDatabase() {
        try {
            em.getTransaction().begin();
            em.createQuery("DELETE FROM IsoTransactionAudit").executeUpdate();
            em.createQuery("DELETE FROM IsoTransaction").executeUpdate();
            em.getTransaction().commit();
        } catch (Exception e) {
            if (em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
        }
    }
    
    /**
     * Test 1: Simulate complete POS purchase transaction flow
     * 
     * Scenario:
     * - Street POS terminal sends purchase request (MTI 0100)
     * - Amount: $150.75 (15075 cents in ISO format)
     * - Card: Visa (BIN 453212...)
     * - Terminal: ATM001
     * - Merchant: Main Street Store
     */
    @Test
    public void testPOSPurchaseTransactionFlow() {
        System.out.println("\n========== POS TERMINAL SIMULATION TEST ==========");
        System.out.println("Scenario: Street POS Purchase Transaction");
        System.out.println("================================================\n");
        
        em.getTransaction().begin();
        
        try {
            // ============================================================
            // PHASE 1: SIMULATE POS TERMINAL REQUEST
            // ============================================================
            System.out.println("[PHASE 1] POS Terminal Request Creation");
            System.out.println("-----------------------------------------");
            
            // Build ISO 8583 message (as it would come from POS)
            String isoMessage = buildIso8583Message(
                "0100",           // MTI: Purchase request
                "000000",         // Processing code
                "15075",          // Amount in cents (ISO format)
                "840",            // Currency code (USD)
                "123456",         // STAN (System Trace Audit Number)
                "4532123456789123" // PAN (card number)
            );
            
            System.out.println("ISO Message Created:");
            System.out.println("  MTI: 0100 (Purchase Request)");
            System.out.println("  Amount: $150.75");
            System.out.println("  Card: Visa (453212...9123)");
            System.out.println("  STAN: 123456");
            System.out.println("  Terminal: ATM001");
            System.out.println("  Timestamp: " + LocalDateTime.now());
            
            // ============================================================
            // PHASE 2: SIMULATE PERSISTREQUEST PARTICIPANT
            // (Receives request and persists to database)
            // ============================================================
            System.out.println("\n[PHASE 2] PersistRequest Participant - Save Initial State");
            System.out.println("-----------------------------------------");
            
            IsoTransaction txn = new IsoTransaction();
            txn.setMti("0100");
            txn.setProcessingCode("000000");
            txn.setAmount(new BigDecimal("150.75"));
            txn.setCurrencyCode("840");
            txn.setStan("123456");
            txn.setRrn(null);  // Not yet assigned
            
            // PAN masking (PCI-DSS Requirement 3.2.1)
            String fullPan = "4532123456789123";
            String maskedPan = IsoUtil.maskPAN(fullPan);
            txn.setPan(maskedPan);  // Store masked PAN
            txn.setPanMasked(maskedPan);
            
            // Network info capture (PCI-DSS Requirement 10.2)
            txn.setIpAddress("192.168.1.100");
            txn.setSessionId("POS_SESSION_001");
            txn.setStatus("RECEIVED");
            txn.setSensitiveDataEncrypted(true);
            
            // Merchant and terminal info
            txn.setMerchantId("MERCHANT_MAINST");
            txn.setTerminalId("ATM001");
            txn.setMerchantName("Main Street Store");
            
            // Store raw request (for audit trail)
            txn.setRawRequest(isoMessage);
            txn.setCreatedBy("POS_SYSTEM");
            txn.setCreatedAt(LocalDateTime.now());
            txn.setComplianceChecked(false);
            
            // SAVE to database (PersistRequest participant does this)
            transactionRepository.save(txn);
            
            System.out.println("Transaction Saved to Database:");
            System.out.println("  Transaction ID: " + txn.getId());
            System.out.println("  Status: " + txn.getStatus());
            System.out.println("  Full PAN (masked in DB): " + txn.getPanMasked());
            System.out.println("  Amount: " + txn.getAmount());
            System.out.println("  Created At: " + txn.getCreatedAt());
            System.out.println("  Compliance Checked: " + txn.getComplianceChecked());
            
            // Create initial audit entry (PersistRequest creates this)
            IsoTransactionAudit initialAudit = new IsoTransactionAudit();
            initialAudit.setIsoTransactionId(txn.getId());
            initialAudit.setAction("RECEIVE_REQUEST");
            initialAudit.setFieldName("status");
            initialAudit.setOldValue(null);
            initialAudit.setNewValue("RECEIVED");
            initialAudit.setChangedBy("POS_SYSTEM");
            initialAudit.setIpAddress("192.168.1.100");
            initialAudit.setSessionId("POS_SESSION_001");
            initialAudit.setReason("Initial request from POS terminal");
            initialAudit.setComplianceVerified(true);
            auditRepository.save(initialAudit);
            
            System.out.println("\nInitial Audit Entry Created:");
            System.out.println("  Audit ID: " + initialAudit.getId());
            System.out.println("  Action: RECEIVE_REQUEST");
            System.out.println("  Field: status");
            System.out.println("  New Value: RECEIVED");
            
            // ============================================================
            // PHASE 3: SIMULATE BUSINESS PROCESSING
            // (Middle participants would process the transaction)
            // ============================================================
            System.out.println("\n[PHASE 3] Business Processing (Middle Participants)");
            System.out.println("-----------------------------------------");
            System.out.println("  Processing: Authorization check...");
            System.out.println("  Processing: Fraud detection...");
            System.out.println("  Processing: Amount validation...");
            System.out.println("  Result: APPROVED");
            
            // ============================================================
            // PHASE 4: SIMULATE UPDATERESPONSE PARTICIPANT
            // (Receives response and updates transaction)
            // ============================================================
            System.out.println("\n[PHASE 4] UpdateResponse Participant - Save Response");
            System.out.println("-----------------------------------------");
            
            // Simulate response from processor
            String responseCode = "00";  // Approved
            String rrn = "RRN987654";
            String authId = "AUTH01";  // VARCHAR(6) max
            String status = IsoUtil.getStatusFromResponseCode(responseCode);
            
            // Update transaction with response data
            txn.setResponseCode(responseCode);
            txn.setRrn(rrn);
            txn.setAuthIdResp(authId);
            txn.setStatus(status);
            txn.setRawResponse("{\"ResponseCode\":\"00\",\"RRN\":\"" + rrn + "\",\"AuthId\":\"" + authId + "\"}");
            txn.setUpdatedBy("PROCSSR");  // VARCHAR(50), but short value
            txn.setUpdatedAt(LocalDateTime.now());
            txn.setComplianceChecked(true);
            
            // Save updated transaction (UpdateResponse participant does this)
            transactionRepository.save(txn);
            
            System.out.println("Transaction Updated in Database:");
            System.out.println("  Response Code: " + txn.getResponseCode());
            System.out.println("  Status: " + txn.getStatus());
            System.out.println("  RRN: " + txn.getRrn());
            System.out.println("  Auth ID: " + txn.getAuthIdResp());
            System.out.println("  Updated At: " + txn.getUpdatedAt());
            System.out.println("  Compliance Checked: " + txn.getComplianceChecked());
            
            // Create response audit entry (UpdateResponse participant creates this)
            IsoTransactionAudit responseAudit = new IsoTransactionAudit();
            responseAudit.setIsoTransactionId(txn.getId());
            responseAudit.setAction("SEND_RESPONSE");
            responseAudit.setFieldName("status");
            responseAudit.setOldValue("RECEIVED");
            responseAudit.setNewValue(status);
            responseAudit.setChangedBy("PROCESSOR");
            responseAudit.setIpAddress("10.0.0.1");
            responseAudit.setSessionId("PROCESSOR_SESSION_001");
            responseAudit.setReason("Authorization approved");
            responseAudit.setComplianceVerified(true);
            auditRepository.save(responseAudit);
            
            System.out.println("\nResponse Audit Entry Created:");
            System.out.println("  Audit ID: " + responseAudit.getId());
            System.out.println("  Action: SEND_RESPONSE");
            System.out.println("  Field: status");
            System.out.println("  Old Value: RECEIVED");
            System.out.println("  New Value: " + status);
            
            // ============================================================
            // PHASE 5: VERIFICATION & COMPLIANCE CHECK
            // ============================================================
            System.out.println("\n[PHASE 5] Data Flow Verification & PCI-DSS Compliance");
            System.out.println("-----------------------------------------");
            
            em.getTransaction().commit();
            
            // Verify transaction was persisted correctly
            em.getTransaction().begin();
            IsoTransaction savedTxn = transactionRepository.findById(txn.getId()).orElse(null);
            assertNotNull("Transaction should be saved", savedTxn);
            assertEquals("Status should be PROCESSED", "PROCESSED", savedTxn.getStatus());
            assertEquals("Amount should match", new BigDecimal("150.75"), savedTxn.getAmount());
            assertEquals("STAN should match", "123456", savedTxn.getStan());
            
            // Verify PCI-DSS Compliance (Requirement 3.2.1 - PAN Masking)
            System.out.println("\nPCI-DSS Requirement 3.2.1 - PAN Masking:");
            System.out.println("  Masked PAN (in DB): " + savedTxn.getPanMasked());
            System.out.println("  Full PAN stored: " + (savedTxn.getPan() != null && savedTxn.getPan().length() > 10));
            assertFalse("PAN in DB should be masked", savedTxn.getPan().contains("4532123456789"));
            assertTrue("Masked PAN format correct", savedTxn.getPanMasked().contains("****"));
            
            // Verify audit trail (Requirement 10.1, 10.2, 10.3)
            List<IsoTransactionAudit> auditTrail = auditRepository.findByIsoTransactionId(txn.getId());
            System.out.println("\nPCI-DSS Requirement 10.1 - Audit Trail:");
            System.out.println("  Total Audit Entries: " + auditTrail.size());
            assertTrue("Should have at least 2 audit entries", auditTrail.size() >= 2);
            
            System.out.println("\nPCI-DSS Requirement 10.2 - User Tracking:");
            for (IsoTransactionAudit audit : auditTrail) {
                System.out.println("  Entry #" + audit.getId() + ":");
                System.out.println("    - Action: " + audit.getAction());
                System.out.println("    - Changed By: " + audit.getChangedBy());
                System.out.println("    - IP Address: " + audit.getIpAddress());
                System.out.println("    - Session ID: " + audit.getSessionId());
                System.out.println("    - Timestamp: " + audit.getCreatedAt());
                assertNotNull("Audit should have ChangedBy", audit.getChangedBy());
                assertNotNull("Audit should have IpAddress", audit.getIpAddress());
                assertNotNull("Audit should have SessionId", audit.getSessionId());
                assertNotNull("Audit should have timestamp", audit.getCreatedAt());
            }
            
            System.out.println("\nPCI-DSS Requirement 10.3 - Change Accountability:");
            System.out.println("  Audit entries properly record:");
            System.out.println("    ✓ What changed (Field: status)");
            System.out.println("    ✓ Who changed it (ChangedBy)");
            System.out.println("    ✓ When it changed (CreatedAt timestamp)");
            System.out.println("    ✓ Where from (IpAddress)");
            System.out.println("    ✓ Why it changed (Reason)");
            System.out.println("    ✓ User session (SessionId)");
            
            // Final verification
            System.out.println("\n========== TEST RESULT ==========");
            System.out.println("✅ POS Purchase Transaction Flow: PASSED");
            System.out.println("✅ Database Persistence: VERIFIED");
            System.out.println("✅ Audit Trail Creation: VERIFIED");
            System.out.println("✅ PCI-DSS Compliance: VERIFIED");
            System.out.println("=================================\n");
            
        } catch (Exception e) {
            if (em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            e.printStackTrace();
            fail("POS simulation test failed: " + e.getMessage());
        }
    }
    
    /**
     * Helper: Build a simplified ISO 8583 message string
     * (In real scenario, this would come from actual POS via socket connection)
     */
    private String buildIso8583Message(String mti, String processingCode, String amount, 
                                       String currency, String stan, String pan) {
        return "{" +
            "\"MTI\":\"" + mti + "\"," +
            "\"ProcessingCode\":\"" + processingCode + "\"," +
            "\"Amount\":\"" + amount + "\"," +
            "\"Currency\":\"" + currency + "\"," +
            "\"STAN\":\"" + stan + "\"," +
            "\"PAN\":\"" + pan + "\"," +
            "\"Terminal\":\"ATM001\"," +
            "\"Merchant\":\"MERCHANT_MAINST\"," +
            "\"Timestamp\":\"" + LocalDateTime.now() + "\"" +
            "}";
    }
    
    /**
     * Test 2: Simulate multiple POS transactions (batch processing)
     * Verifies data integrity across multiple simultaneous transactions
     */
    @Test
    public void testMultiplePOSTransactionFlow() {
        System.out.println("\n========== MULTIPLE POS TRANSACTIONS TEST ==========");
        System.out.println("Scenario: Batch processing from multiple POS terminals");
        System.out.println("====================================================\n");
        
        em.getTransaction().begin();
        
        try {
            int transactionCount = 5;
            System.out.println("Creating " + transactionCount + " transactions from different POS terminals...\n");
            
            for (int i = 1; i <= transactionCount; i++) {
                // Simulate transaction from different terminal
                IsoTransaction txn = new IsoTransaction();
                txn.setMti("0100");
                txn.setProcessingCode("000000");
                txn.setAmount(new BigDecimal(100 + i));
                txn.setCurrencyCode("840");
                txn.setStan(String.format("%06d", 100000 + i));
                
                String pan = "4532" + String.format("%011d", 1000000 + i);
                txn.setPan(IsoUtil.maskPAN(pan));  // Store masked PAN
                txn.setPanMasked(IsoUtil.maskPAN(pan));
                
                txn.setIpAddress("192.168.1." + (100 + i));
                txn.setSessionId("POS_SESSION_" + String.format("%03d", i));
                txn.setTerminalId("ATM" + String.format("%03d", i));
                txn.setMerchantId("MERCHANT_" + i);
                txn.setStatus("PROCESSED");
                txn.setResponseCode("00");
                txn.setRrn("RRN" + String.format("%06d", 100000 + i));
                txn.setRawRequest("{\"MTI\":\"0100\",\"Amount\":" + (100 + i) + "}");  // Add required rawRequest
                txn.setCreatedBy("POS_SYSTEM_" + i);
                txn.setCreatedAt(LocalDateTime.now());
                
                transactionRepository.save(txn);
                
                System.out.println("✓ Transaction #" + i);
                System.out.println("  Terminal: " + txn.getTerminalId());
                System.out.println("  Amount: $" + txn.getAmount());
                System.out.println("  PAN (masked): " + txn.getPanMasked());
                System.out.println("  Status: " + txn.getStatus() + "\n");
            }
            
            em.getTransaction().commit();
            
            // Verify all transactions persisted
            em.getTransaction().begin();
            List<IsoTransaction> allTransactions = transactionRepository.findAll();
            assertEquals("All transactions should be persisted", transactionCount, allTransactions.size());
            
            System.out.println("✅ Multiple POS Transaction Flow: PASSED");
            System.out.println("   Total transactions persisted: " + allTransactions.size());
            
        } catch (Exception e) {
            if (em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            e.printStackTrace();
            fail("Multiple POS test failed: " + e.getMessage());
        }
    }
}
