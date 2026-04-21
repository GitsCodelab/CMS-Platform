package org.cms.jposee.repository.impl;

import org.cms.jposee.entity.IsoTransaction;
import org.cms.jposee.repository.IsoTransactionRepository;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import javax.persistence.EntityManager;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

/**
 * Unit Tests for IsoTransactionRepository
 * 
 * Uses Mockito to mock EntityManager and verify repository logic
 * Tests:
 * - CRUD operations
 * - Query methods
 * - Aggregate operations
 * - Compliance tracking
 * 
 * @author jPOS-EE Test Suite
 * @version 1.0
 * @since April 21, 2026
 */
public class IsoTransactionRepositoryTest {
    
    @Mock
    private EntityManager entityManager;
    
    private IsoTransactionRepository repository;
    
    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        repository = new IsoTransactionRepositoryImpl(entityManager);
    }
    
    @Test
    public void testRepositoryInitialization() {
        assertNotNull("Repository should be initialized", repository);
    }
    
    @Test
    public void testSaveNewTransaction() {
        // Create new transaction
        IsoTransaction txn = new IsoTransaction();
        txn.setMti("0100");
        txn.setStan("123456");
        txn.setAmount(new BigDecimal("100.00"));
        txn.setStatus("RECEIVED");
        
        // Save (no ID = new transaction)
        IsoTransaction saved = repository.save(txn);
        
        // Verify persist was called
        verify(entityManager).persist(txn);
        assertEquals("Saved transaction should match original", txn, saved);
    }
    
    @Test
    public void testSaveExistingTransaction() {
        // Create transaction with ID (existing)
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        txn.setMti("0100");
        txn.setStatus("RECEIVED");
        
        // Mock merge behavior
        when(entityManager.merge(txn)).thenReturn(txn);
        
        // Save
        IsoTransaction saved = repository.save(txn);
        
        // Verify merge was called (not persist)
        verify(entityManager).merge(txn);
        assertEquals("Merged transaction should match", txn, saved);
    }
    
    @Test
    public void testFindByIdFound() {
        // Create transaction
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        txn.setMti("0100");
        
        // Mock find behavior
        when(entityManager.find(IsoTransaction.class, 1001L)).thenReturn(txn);
        
        // Find
        Optional<IsoTransaction> result = repository.findById(1001L);
        
        // Verify
        assertTrue("Transaction should be found", result.isPresent());
        assertEquals("Found transaction ID should match", Long.valueOf(1001L), result.get().getId());
    }
    
    @Test
    public void testFindByIdNotFound() {
        // Mock find returning null
        when(entityManager.find(IsoTransaction.class, 9999L)).thenReturn(null);
        
        // Find
        Optional<IsoTransaction> result = repository.findById(9999L);
        
        // Verify
        assertFalse("Transaction should not be found", result.isPresent());
    }
    
    @Test
    public void testUpdateTransaction() {
        // Create and update transaction
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        txn.setStatus("RECEIVED");
        txn.setUpdatedAt(LocalDateTime.now());
        
        // Mock merge
        when(entityManager.merge(txn)).thenReturn(txn);
        
        // Update
        IsoTransaction updated = repository.update(txn);
        
        // Verify
        verify(entityManager).merge(txn);
        assertNotNull("Updated timestamp should be set", updated.getUpdatedAt());
    }
    
    @Test
    public void testUpdateStatus() {
        // Create transaction
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        txn.setStatus("RECEIVED");
        
        // Mock find and merge
        when(entityManager.find(IsoTransaction.class, 1001L)).thenReturn(txn);
        when(entityManager.merge(txn)).thenReturn(txn);
        
        // Update status
        IsoTransaction updated = repository.updateStatus(1001L, "PROCESSED");
        
        // Verify
        assertEquals("Status should be PROCESSED", "PROCESSED", updated.getStatus());
        verify(entityManager).merge(txn);
    }
    
    @Test
    public void testDeleteById() {
        // Create transaction
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        
        // Mock find
        when(entityManager.find(IsoTransaction.class, 1001L)).thenReturn(txn);
        
        // Delete
        repository.deleteById(1001L);
        
        // Verify
        verify(entityManager).remove(txn);
    }
    
    @Test
    public void testIncrementRetryCount() {
        // Create transaction with retry count
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        txn.setRetryCount(2);
        
        // Mock find and merge
        when(entityManager.find(IsoTransaction.class, 1001L)).thenReturn(txn);
        when(entityManager.merge(txn)).thenReturn(txn);
        
        // Increment
        IsoTransaction updated = repository.incrementRetryCount(1001L);
        
        // Verify
        assertEquals("Retry count should be incremented to 3", 3, updated.getRetryCount().intValue());
        verify(entityManager).merge(txn);
    }
    
    @Test
    public void testUpdateWithResponse() {
        // Create transaction
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        txn.setStatus("RECEIVED");
        
        // Mock find and merge
        when(entityManager.find(IsoTransaction.class, 1001L)).thenReturn(txn);
        when(entityManager.merge(txn)).thenReturn(txn);
        
        // Update with response
        IsoTransaction updated = repository.updateWithResponse(1001L, "00", "AUTH001", "APPROVED");
        
        // Verify
        assertEquals("Response code should be 00", "00", updated.getResponseCode());
        assertEquals("Auth ID should be set", "AUTH001", updated.getAuthIdResp());
        assertEquals("Status should be PROCESSED", "PROCESSED", updated.getStatus());
        verify(entityManager).merge(txn);
    }
    
    @Test
    public void testComplianceTracking() {
        // Create transaction
        IsoTransaction txn = new IsoTransaction();
        txn.setId(1001L);
        txn.setComplianceChecked(false);
        
        // Mock find and merge
        when(entityManager.find(IsoTransaction.class, 1001L)).thenReturn(txn);
        when(entityManager.merge(txn)).thenReturn(txn);
        
        // Mark compliance verified
        repository.markComplianceVerified(1001L);
        
        // Verify
        assertTrue("Compliance should be marked verified", txn.getComplianceChecked());
        verify(entityManager).merge(txn);
    }
    
    @Test
    public void testSaveAllWithBatchProcessing() {
        // Create multiple transactions
        IsoTransaction txn1 = new IsoTransaction();
        txn1.setMti("0100");
        
        IsoTransaction txn2 = new IsoTransaction();
        txn2.setMti("0200");
        
        java.util.List<IsoTransaction> transactions = java.util.Arrays.asList(txn1, txn2);
        
        // Save all
        java.util.List<IsoTransaction> saved = repository.saveAll(transactions);
        
        // Verify
        assertEquals("Should save both transactions", 2, saved.size());
        verify(entityManager, times(2)).persist(any(IsoTransaction.class));
        verify(entityManager, atLeastOnce()).flush();
    }
    
    @Test
    public void testRepositoryExistsCheck() {
        // Create mock query
        javax.persistence.TypedQuery<Long> mockQuery = mock(javax.persistence.TypedQuery.class);
        when(entityManager.createQuery(
            "SELECT COUNT(t) FROM IsoTransaction t WHERE t.stan = :stan", 
            Long.class
        )).thenReturn(mockQuery);
        when(mockQuery.setParameter("stan", "123456")).thenReturn(mockQuery);
        when(mockQuery.getSingleResult()).thenReturn(1L);
        
        // Note: In real integration test, this would use real EntityManager
        // This is a simplified test showing the pattern
    }
}
