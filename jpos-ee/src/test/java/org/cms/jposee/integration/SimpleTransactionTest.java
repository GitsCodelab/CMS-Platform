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
import java.util.Random;

import static org.junit.Assert.*;

/**
 * Simple Transaction Test - Creates 200 transactions for testing
 */
public class SimpleTransactionTest {
    
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
    
    @Test
    public void testCreate200Transactions() {
        System.out.println("\n========== SIMPLE TRANSACTION TEST: 200 TXN ==========");
        
        long startTime = System.currentTimeMillis();
        int successCount = 0;
        int failureCount = 0;
        
        try {
            em.getTransaction().begin();
            
            for (int i = 1; i <= 200; i++) {
                try {
                    // Create transaction
                    IsoTransaction txn = createTestTransaction(i);
                    transactionRepository.save(txn);
                    
                    successCount++;
                    
                    if (i % 50 == 0) {
                        System.out.println("  [" + i + "/200] transactions created");
                    }
                    
                } catch (Exception e) {
                    failureCount++;
                    System.err.println("  Failed at transaction " + i + ": " + e.getMessage());
                    e.printStackTrace();
                }
            }
            
            em.getTransaction().commit();
            
        } catch (Exception e) {
            if (em.getTransaction().isActive()) {
                em.getTransaction().rollback();
            }
            e.printStackTrace();
            fail("Transaction test failed: " + e.getMessage());
        }
        
        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        
        // Results
        System.out.println("\n========== TEST RESULTS ==========");
        System.out.println("Total Transactions: 200");
        System.out.println("Successful: " + successCount);
        System.out.println("Failed: " + failureCount);
        System.out.println("Duration: " + duration + " ms");
        System.out.println("Throughput: " + (200000.0 / duration) + " txn/sec");
        System.out.println("===================================\n");
        
        assertEquals("All 200 transactions should succeed", 200, successCount);
        assertEquals("No failures expected", 0, failureCount);
        assertTrue("Should complete in reasonable time", duration < 60000); // 60 seconds
    }
    
    private IsoTransaction createTestTransaction(int index) {
        IsoTransaction txn = new IsoTransaction();
        
        // Generate unique values
        String stan = String.format("%012d", index);  // VARCHAR(12)
        String pan = "4532" + String.format("%011d", index);  // VARCHAR(19)
        String rrn = String.format("%012d", index);  // VARCHAR(12) - numeric only
        
        txn.setMti("0100");
        txn.setProcessingCode("000000");
        txn.setAmount(new BigDecimal(String.valueOf(100 + (random.nextInt(9900)))));
        txn.setCurrencyCode("840"); // USD
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
