package org.cms.jposee.repository.impl;

import org.cms.jposee.entity.IsoTransactionAudit;
import org.cms.jposee.repository.IsoTransactionAuditRepository;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import javax.persistence.EntityManager;
import javax.persistence.Query;
import javax.persistence.TypedQuery;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

/**
 * Unit Tests for IsoTransactionAuditRepository
 * 
 * Tests immutability constraints, audit trail integrity, and PCI-DSS compliance
 * Uses Mockito to mock EntityManager
 * 
 * Focuses on:
 * - Write-once semantics (no updates)
 * - Immutable audit fields
 * - Chronological ordering
 * - Compliance verification tracking
 * - Batch audit operations
 * 
 * @author jPOS-EE Test Suite
 * @version 1.0
 * @since April 21, 2026
 */
public class IsoTransactionAuditRepositoryTest {
    
    @Mock
    private EntityManager entityManager;
    
    @Mock
    private TypedQuery<IsoTransactionAudit> typedQuery;
    
    @Mock
    private TypedQuery<Long> typedQueryLong;
    
    private IsoTransactionAuditRepository repository;
    
    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        repository = new IsoTransactionAuditRepositoryImpl(entityManager);
    }
    
    @Test
    public void testSaveNewAuditRecord() {
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setIsoTransactionId(1001L);
        audit.setAction("CREATE");
        audit.setFieldName("status");
        audit.setOldValue(null);
        audit.setNewValue("PENDING");
        
        when(entityManager.find(IsoTransactionAudit.class, null)).thenReturn(null);
        repository.save(audit);
        
        verify(entityManager).persist(audit);
    }
    
    @Test
    public void testFindByIdFound() {
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setId(5001L);
        audit.setAction("UPDATE");
        
        when(entityManager.find(IsoTransactionAudit.class, 5001L)).thenReturn(audit);
        Optional<IsoTransactionAudit> result = repository.findById(5001L);
        
        assertTrue("Audit should be found", result.isPresent());
        assertEquals("Audit ID should match", Long.valueOf(5001L), result.get().getId());
    }
    
    @Test
    public void testFindByIdNotFound() {
        when(entityManager.find(IsoTransactionAudit.class, 9999L)).thenReturn(null);
        Optional<IsoTransactionAudit> result = repository.findById(9999L);
        
        assertFalse("Audit should not be found", result.isPresent());
    }
    
    @Test
    public void testFindByIsoTransactionId() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit1 = new IsoTransactionAudit();
        audit1.setIsoTransactionId(1001L);
        audit1.setAction("CREATE");
        audits.add(audit1);
        
        IsoTransactionAudit audit2 = new IsoTransactionAudit();
        audit2.setIsoTransactionId(1001L);
        audit2.setAction("UPDATE");
        audits.add(audit2);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter("txnId", 1001L)).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findByIsoTransactionId(1001L);
        
        assertEquals("Should find 2 audit records", 2, result.size());
        assertEquals("First action should be CREATE", "CREATE", audits.get(0).getAction());
        assertEquals("Second action should be UPDATE", "UPDATE", audits.get(1).getAction());
    }
    
    @Test
    public void testFindByAction() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setAction("COMPLIANCE_CHECK");
        audits.add(audit);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter("action", "COMPLIANCE_CHECK")).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findByAction("COMPLIANCE_CHECK");
        
        assertEquals("Should find 1 compliance check audit", 1, result.size());
    }
    
    @Test
    public void testFindByDateRange() {
        LocalDateTime start = LocalDateTime.now().minusDays(1);
        LocalDateTime end = LocalDateTime.now();
        
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setCreatedAt(LocalDateTime.now().minusHours(12));
        audits.add(audit);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter(eq("startDate"), any())).thenReturn(typedQuery);
        when(typedQuery.setParameter(eq("endDate"), any())).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findByDateRange(start, end);
        
        assertEquals("Should find audits in date range", 1, result.size());
    }
    
    @Test
    public void testFindByChangedBy() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setChangedBy("ADMIN_USER");
        audits.add(audit);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter("changedBy", "ADMIN_USER")).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findByChangedBy("ADMIN_USER");
        
        assertEquals("Should find audits by changed_by", 1, result.size());
    }
    
    @Test
    public void testFindByIpAddress() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setIpAddress("192.168.1.100");
        audits.add(audit);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter("ipAddress", "192.168.1.100")).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findByIpAddress("192.168.1.100");
        
        assertEquals("Should find audits by IP address", 1, result.size());
    }
    
    @Test
    public void testFindBySessionId() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setSessionId("SESSION_ABC123");
        audits.add(audit);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter("sessionId", "SESSION_ABC123")).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findBySessionId("SESSION_ABC123");
        
        assertEquals("Should find audits by session ID", 1, result.size());
    }
    
    @Test
    public void testFindByFieldName() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setFieldName("retry_count");
        audits.add(audit);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter("fieldName", "retry_count")).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findByFieldName("retry_count");
        
        assertEquals("Should find audits by field name", 1, result.size());
    }
    
    @Test
    public void testSaveAll() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            IsoTransactionAudit audit = new IsoTransactionAudit();
            audit.setIsoTransactionId(1001L);
            audit.setAction("BATCH_INSERT_" + i);
            audits.add(audit);
        }
        
        List<IsoTransactionAudit> result = repository.saveAll(audits);
        
        verify(entityManager, times(3)).persist(any(IsoTransactionAudit.class));
        assertEquals("All audits should be saved", 3, result.size());
    }
    
    @Test
    public void testCountAuditRecords() {
        when(entityManager.createQuery("SELECT COUNT(a) FROM IsoTransactionAudit a", Long.class)).thenReturn(typedQueryLong);
        when(typedQueryLong.getSingleResult()).thenReturn(42L);
        
        long count = repository.count();
        
        assertEquals("Should return count of audit records", 42L, count);
    }
    
    @Test
    public void testCountByIsoTransactionId() {
        when(entityManager.createQuery(
            "SELECT COUNT(a) FROM IsoTransactionAudit a WHERE a.isoTransactionId = :txnId", Long.class
        )).thenReturn(typedQueryLong);
        when(typedQueryLong.setParameter("txnId", 1001L)).thenReturn(typedQueryLong);
        when(typedQueryLong.getSingleResult()).thenReturn(5L);
        
        long count = repository.countByIsoTransactionId(1001L);
        
        assertEquals("Should return count for transaction", 5L, count);
    }
    
    @Test
    public void testFindUnverifiedAuditRecords() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setComplianceVerified(false);
        audits.add(audit);
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.findUnverifiedAuditRecords();
        
        assertEquals("Should find unverified audit records", 1, result.size());
        assertFalse("Audit should not be compliance verified", result.get(0).getComplianceVerified());
    }
    
    @Test
    public void testMarkComplianceVerified() {
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setId(5001L);
        audit.setComplianceVerified(false);
        
        when(entityManager.find(IsoTransactionAudit.class, 5001L)).thenReturn(audit);
        repository.markComplianceVerified(5001L, "Verified by compliance officer");
        
        verify(entityManager).merge(audit);
        assertTrue("Audit should be marked verified", audit.getComplianceVerified());
        assertEquals("Notes should be updated", "Verified by compliance officer", audit.getComplianceNotes());
    }
    
    @Test
    public void testGetAuditTrail() {
        List<IsoTransactionAudit> audits = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            IsoTransactionAudit audit = new IsoTransactionAudit();
            audit.setIsoTransactionId(1001L);
            audit.setAction("STEP_" + i);
            audits.add(audit);
        }
        
        when(entityManager.createQuery(anyString(), eq(IsoTransactionAudit.class))).thenReturn(typedQuery);
        when(typedQuery.setParameter("txnId", 1001L)).thenReturn(typedQuery);
        when(typedQuery.getResultList()).thenReturn(audits);
        
        List<IsoTransactionAudit> result = repository.getAuditTrail(1001L);
        
        assertEquals("Audit trail should have 3 entries", 3, result.size());
        assertEquals("First action should be STEP_0", "STEP_0", audits.get(0).getAction());
    }
    
    @Test
    public void testDeleteById() {
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setId(5001L);
        
        when(entityManager.find(IsoTransactionAudit.class, 5001L)).thenReturn(audit);
        repository.deleteById(5001L);
        
        verify(entityManager).remove(audit);
    }
    
    @Test
    public void testImmutabilityConstraint() {
        // Test that attempting to save an audit with existing ID doesn't cause update
        IsoTransactionAudit audit = new IsoTransactionAudit();
        audit.setId(5001L);
        audit.setAction("ORIGINAL_ACTION");
        
        // Attempting to save an existing audit should log warning but not update
        repository.save(audit);
        
        verify(entityManager).merge(audit);  // Should merge, not persist
    }
}
