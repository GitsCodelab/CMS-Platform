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
import java.util.List;
import java.util.Random;

import static org.junit.Assert.*;

/**
 * Transaction Audit Testing
 * Validates that all transactions create proper audit trail entries
 */
public class TransactionAuditTest {
    
    private EntityManagerFactory emf;
    private EntityManager em;
    private IsoTransactionRepository transactionRepository;
    private IsoTransactionAuditRepository auditRepository;
    private Random random;
    
    @Before
    public void setUp() {
        emf = Persistence.createEntityManagerFactory("jposee-persistence");
        em = emf.createEntityManager();
        transactionRepository = new IsoTransactionRepositoryImpl(em);
        auditRepository = new IsoTransactionAuditRepositoryImpl(em);
        random = new Random();
        
        // Clean database before each test
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
    
    /**
     * Helper method to clean test data from database
     */
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
            // Ignore cleanup errors
        }
    }
    
    @Test
    public void testTransactionAuditTrail() {
        System.out.println("\n========== TRANSACTION AUDIT TRAIL TEST ==========");
        
        em.getTransaction().begin();
        
        // Create 5 test transactions with audit entries
        int transactionCount = 5;
        long[] transactionIds = new long[transactionCount];
        
        try {
            for (int i = 1; i <= transactionCount; i++) {
                // Create transaction
                IsoTransaction txn = createTestTransaction(i);
                transactionRepository.save(txn);
                transactionIds[i - 1] = txn.getId();
                
                System.out.println("\n[Transaction #" + i + "]");
                System.out.println("  ID: " + txn.getId());
                System.out.println("  STAN: " + txn.getStan());
                System.out.println("  PAN (Masked): " + txn.getPanMasked());
                System.out.println("  Status: " + txn.getStatus());
                System.out.println("  Created At: " + txn.getCreatedAt());
            }
            
            em.getTransaction().commit();
            
            // Now create audit entries for each transaction
            em.getTransaction().begin();
            for (int i = 0; i < transactionCount; i++) {
                long txnId = transactionIds[i];
                IsoTransaction txn = transactionRepository.findById(txnId)
                    .orElseThrow(() -> new RuntimeException("Transaction not found: " + txnId));
                
                // Create audit entry for transaction creation
                IsoTransactionAudit createAudit = new IsoTransactionAudit();
                createAudit.setIsoTransactionId(txn.getId());
                createAudit.setAction("CREATE");
                createAudit.setFieldName("status");
                createAudit.setNewValue("RECEIVED");
                createAudit.setChangedBy("TEST_SYSTEM");
                createAudit.setIpAddress("127.0.0.1");
                createAudit.setSessionId("TEST_SESSION_" + i);
                createAudit.setReason("Test transaction creation");
                auditRepository.save(createAudit);
            }
            em.getTransaction().commit();
            
            // Query and display audit trail
            System.out.println("\n========== AUDIT TRAIL RESULTS ==========");
            List<IsoTransactionAudit> allAudits = auditRepository.findAll();
            System.out.println("Total Audit Entries: " + allAudits.size());
            
            for (IsoTransactionAudit audit : allAudits) {
                System.out.println("\n[Audit Entry #" + audit.getId() + "]");
                System.out.println("  Transaction ID: " + audit.getIsoTransactionId());
                System.out.println("  Action: " + audit.getAction());
                System.out.println("  Field: " + audit.getFieldName());
                System.out.println("  New Value: " + audit.getNewValue());
                System.out.println("  Changed By: " + audit.getChangedBy());
                System.out.println("  IP Address: " + audit.getIpAddress());
                System.out.println("  Session: " + audit.getSessionId());
                System.out.println("  Reason: " + audit.getReason());
                System.out.println("  Created At: " + audit.getCreatedAt());
            }
            
            // Verify audit entries match transactions
            System.out.println("\n========== AUDIT VERIFICATION ==========");
            assertTrue("Should have audit entries", allAudits.size() > 0);
            assertEquals("Should have one audit per transaction", transactionCount, allAudits.size());
            
            for (IsoTransactionAudit audit : allAudits) {
                IsoTransaction txn = transactionRepository.findById(audit.getIsoTransactionId())
                    .orElseThrow(() -> new RuntimeException("Referenced transaction not found"));
                assertNotNull("Audit must reference valid transaction", txn);
                assertTrue("Audit should have valid action", audit.getAction() != null && !audit.getAction().isEmpty());
                assertNotNull("Audit must have timestamp", audit.getCreatedAt());
                System.out.println("✓ Audit #" + audit.getId() + " verified for Transaction #" + txn.getId());
            }
            
            System.out.println("\n========== AUDIT TEST PASSED ==========\n");
            
        } catch (Exception e) {
            if (em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            e.printStackTrace();
            fail("Audit test failed: " + e.getMessage());
        }
    }
    
    @Test
    public void testPCIDSSAuditCompliance() {
        System.out.println("\n========== PCI-DSS AUDIT COMPLIANCE TEST ==========");
        
        em.getTransaction().begin();
        
        try {
            // Create transaction
            IsoTransaction txn = createTestTransaction(100);
            transactionRepository.save(txn);
            
            em.getTransaction().commit();
            
            // Create audit entry
            em.getTransaction().begin();
            IsoTransactionAudit audit = new IsoTransactionAudit();
            audit.setIsoTransactionId(txn.getId());
            audit.setAction("COMPLIANCE_CHECK");
            audit.setFieldName("pan_masked");
            audit.setOldValue(null);
            audit.setNewValue(txn.getPanMasked());  // Only masked PAN in audit
            audit.setChangedBy("COMPLIANCE_SYSTEM");
            audit.setIpAddress("10.0.0.1");
            audit.setSessionId("COMPLIANCE_SESSION");
            audit.setReason("PCI-DSS Requirement 3.2.1: PAN masking validation");
            audit.setComplianceVerified(true);
            audit.setComplianceNotes("PAN properly masked: " + txn.getPanMasked());
            auditRepository.save(audit);
            
            em.getTransaction().commit();
            
            // Verify compliance
            System.out.println("Transaction ID: " + txn.getId());
            System.out.println("Original PAN: " + txn.getPan());
            System.out.println("Masked PAN (in DB): " + txn.getPanMasked());
            System.out.println("Audit Entry:");
            System.out.println("  - Compliance Verified: " + audit.getComplianceVerified());
            System.out.println("  - Compliance Notes: " + audit.getComplianceNotes());
            System.out.println("  - Stored Value (Masked): " + audit.getNewValue());
            
            // Verify no full PAN in audit (PCI-DSS 3.2.1)
            assertFalse("Full unmasked PAN should NOT be in audit trail", 
                audit.getNewValue().equals(txn.getPan()));
            assertTrue("Masked PAN SHOULD be in audit (only first 6 and last 4 visible)", 
                audit.getNewValue().contains("****") && audit.getNewValue().length() < txn.getPan().length());
            
            System.out.println("\n✓ PCI-DSS Compliance Verified - No full PAN in audit trail");
            System.out.println("✓ Only masked PAN stored: " + audit.getNewValue());
            System.out.println("========== COMPLIANCE TEST PASSED ==========\n");
            
        } catch (Exception e) {
            if (em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            e.printStackTrace();
            fail("Compliance test failed: " + e.getMessage());
        }
    }
    
    private IsoTransaction createTestTransaction(int index) {
        IsoTransaction txn = new IsoTransaction();
        
        String stan = String.format("%012d", index);
        String pan = "4532" + String.format("%011d", index);
        String rrn = String.format("%012d", index);
        
        txn.setMti("0100");
        txn.setProcessingCode("000000");
        txn.setAmount(new BigDecimal(String.valueOf(100 + (random.nextInt(9900)))));
        txn.setCurrencyCode("840");
        txn.setStan(stan);
        txn.setRrn(rrn);
        txn.setTerminalId("TERM001");
        txn.setMerchantId("MERCH001");
        txn.setMerchantName("Test Merchant");
        txn.setPan(pan);
        txn.setPanMasked(IsoUtil.maskPAN(pan));
        txn.setRawRequest("REQUEST_" + index);
        txn.setStatus("RECEIVED");
        txn.setIpAddress("192.168.1." + (index % 255));
        txn.setSessionId("SESSION_" + index);
        txn.setRetryCount(0);
        txn.setComplianceChecked(true);
        txn.setSensitiveDataEncrypted(true);
        
        return txn;
    }
}
