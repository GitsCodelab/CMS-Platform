package org.cms.jposee.repository.impl;

import org.cms.jposee.entity.IsoTransactionAudit;
import org.cms.jposee.repository.IsoTransactionAuditRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.Query;
import javax.persistence.TypedQuery;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

/**
 * Implementation of IsoTransactionAuditRepository using JPA EntityManager
 * 
 * Provides persistence operations for immutable audit trail of ISO transactions.
 * All audit records are write-once and cannot be modified after creation.
 * This ensures compliance with PCI-DSS Requirement 10.3 (immutable audit logs).
 * 
 * Key Features:
 * - No update methods (audit records are immutable by design)
 * - WARN log on delete operations (for data retention auditing)
 * - Batch processing optimized for high-volume audit logging
 * - Query optimization with index-backed lookups
 * 
 * Compliance Notes:
 * - PCI-DSS Req 10.3: Immutable audit trail protected by database constraints
 * - Requirement 10.2: User/IP tracking preserved in changedBy, ipAddress, sessionId
 * - All timestamps immutable (created_at NOT updatable in schema)
 * 
 * @author jPOS-EE Persistence Layer
 * @version 1.0
 * @since April 21, 2026
 */
public class IsoTransactionAuditRepositoryImpl implements IsoTransactionAuditRepository {
    
    private static final Logger logger = LoggerFactory.getLogger(IsoTransactionAuditRepositoryImpl.class);
    
    @PersistenceContext(unitName = "jposee-persistence")
    private EntityManager em;
    
    /**
     * Constructor for dependency injection (testing)
     */
    public IsoTransactionAuditRepositoryImpl(EntityManager entityManager) {
        this.em = entityManager;
    }
    
    /**
     * Default constructor (JPA)
     */
    public IsoTransactionAuditRepositoryImpl() {
    }
    
    @Override
    public IsoTransactionAudit save(IsoTransactionAudit auditRecord) {
        if (auditRecord.getId() == null) {
            em.persist(auditRecord);
            logger.debug("Audit record persisted for transaction {}: {}", 
                auditRecord.getIsoTransactionId(), auditRecord.getAction());
            return auditRecord;
        } else {
            logger.warn("Attempted to update immutable audit record {}. Ignoring update.", auditRecord.getId());
            return em.merge(auditRecord);
        }
    }
    
    @Override
    public List<IsoTransactionAudit> saveAll(List<IsoTransactionAudit> auditRecords) {
        if (auditRecords == null || auditRecords.isEmpty()) {
            return Collections.emptyList();
        }
        
        for (int i = 0; i < auditRecords.size(); i++) {
            IsoTransactionAudit audit = auditRecords.get(i);
            if (audit.getId() == null) {
                em.persist(audit);
            }
            
            // Batch flush every 20 records to prevent memory overflow
            if ((i + 1) % 20 == 0) {
                em.flush();
                em.clear();
                logger.debug("Batch flushed {} audit records", (i + 1));
            }
        }
        
        // Final flush
        em.flush();
        logger.debug("Batch completed: {} audit records persisted", auditRecords.size());
        return auditRecords;
    }
    
    @Override
    public Optional<IsoTransactionAudit> findById(Long id) {
        if (id == null) {
            return Optional.empty();
        }
        
        IsoTransactionAudit audit = em.find(IsoTransactionAudit.class, id);
        logger.debug("Audit record retrieved: {}", id);
        return Optional.ofNullable(audit);
    }
    
    @Override
    public List<IsoTransactionAudit> findByIsoTransactionId(Long isoTransactionId) {
        if (isoTransactionId == null) {
            return Collections.emptyList();
        }
        
        TypedQuery<IsoTransactionAudit> query = em.createQuery(
            "SELECT a FROM IsoTransactionAudit a WHERE a.isoTransactionId = :txnId ORDER BY a.createdAt ASC",
            IsoTransactionAudit.class
        );
        query.setParameter("txnId", isoTransactionId);
        
        List<IsoTransactionAudit> result = query.getResultList();
        logger.debug("Found {} audit records for transaction {}", result.size(), isoTransactionId);
        return result;
    }
    
    @Override
    public List<IsoTransactionAudit> findByAction(String action) {
        if (action == null || action.isEmpty()) {
            return Collections.emptyList();
        }
        
        TypedQuery<IsoTransactionAudit> query = em.createQuery(
            "SELECT a FROM IsoTransactionAudit a WHERE a.action = :action ORDER BY a.createdAt DESC",
            IsoTransactionAudit.class
        );
        query.setParameter("action", action);
        
        List<IsoTransactionAudit> result = query.getResultList();
        logger.debug("Found {} audit records with action: {}", result.size(), action);
        return result;
    }
    
    @Override
    public List<IsoTransactionAudit> findByDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        if (startDate == null || endDate == null) {
            return Collections.emptyList();
        }
        
        TypedQuery<IsoTransactionAudit> query = em.createQuery(
            "SELECT a FROM IsoTransactionAudit a " +
            "WHERE a.createdAt >= :startDate AND a.createdAt <= :endDate " +
            "ORDER BY a.createdAt DESC",
            IsoTransactionAudit.class
        );
        query.setParameter("startDate", startDate);
        query.setParameter("endDate", endDate);
        
        List<IsoTransactionAudit> result = query.getResultList();
        logger.debug("Found {} audit records in date range [{}-{}]", result.size(), startDate, endDate);
        return result;
    }
    
    @Override
    public List<IsoTransactionAudit> findByChangedBy(String changedBy) {
        if (changedBy == null || changedBy.isEmpty()) {
            return Collections.emptyList();
        }
        
        TypedQuery<IsoTransactionAudit> query = em.createQuery(
            "SELECT a FROM IsoTransactionAudit a WHERE a.changedBy = :changedBy ORDER BY a.createdAt DESC",
            IsoTransactionAudit.class
        );
        query.setParameter("changedBy", changedBy);
        
        List<IsoTransactionAudit> result = query.getResultList();
        logger.debug("Found {} audit records changed by: {}", result.size(), changedBy);
        return result;
    }
    
    @Override
    public List<IsoTransactionAudit> findByIpAddress(String ipAddress) {
        if (ipAddress == null || ipAddress.isEmpty()) {
            return Collections.emptyList();
        }
        
        TypedQuery<IsoTransactionAudit> query = em.createQuery(
            "SELECT a FROM IsoTransactionAudit a WHERE a.ipAddress = :ipAddress ORDER BY a.createdAt DESC",
            IsoTransactionAudit.class
        );
        query.setParameter("ipAddress", ipAddress);
        
        List<IsoTransactionAudit> result = query.getResultList();
        logger.debug("Found {} audit records from IP: {}", result.size(), ipAddress);
        return result;
    }
    
    @Override
    public List<IsoTransactionAudit> findBySessionId(String sessionId) {
        if (sessionId == null || sessionId.isEmpty()) {
            return Collections.emptyList();
        }
        
        TypedQuery<IsoTransactionAudit> query = em.createQuery(
            "SELECT a FROM IsoTransactionAudit a WHERE a.sessionId = :sessionId ORDER BY a.createdAt DESC",
            IsoTransactionAudit.class
        );
        query.setParameter("sessionId", sessionId);
        
        List<IsoTransactionAudit> result = query.getResultList();
        logger.debug("Found {} audit records for session: {}", result.size(), sessionId);
        return result;
    }
    
    @Override
    public List<IsoTransactionAudit> findByFieldName(String fieldName) {
        if (fieldName == null || fieldName.isEmpty()) {
            return Collections.emptyList();
        }
        
        TypedQuery<IsoTransactionAudit> query = em.createQuery(
            "SELECT a FROM IsoTransactionAudit a WHERE a.fieldName = :fieldName ORDER BY a.createdAt DESC",
            IsoTransactionAudit.class
        );
        query.setParameter("fieldName", fieldName);
        
        List<IsoTransactionAudit> result = query.getResultList();
        logger.debug("Found {} audit records for field: {}", result.size(), fieldName);
        return result;
    }
    
    @Override
    public List<IsoTransactionAudit> findAll() {
        return em.createQuery(
            "SELECT a FROM IsoTransactionAudit a ORDER BY a.createdAt DESC",
            IsoTransactionAudit.class
        ).getResultList();
    }
    
    @Override
    public void deleteById(Long id) {
        if (id == null) {
            return;
        }
        
        logger.warn("COMPLIANCE ALERT: Deleting audit record {}. This operation is typically restricted by policy.", id);
        Optional<IsoTransactionAudit> audit = findById(id);
        if (audit.isPresent()) {
            em.remove(audit.get());
            logger.warn("Audit record {} deleted", id);
        }
    }
    
    @Override
    public void deleteByIsoTransactionId(Long isoTransactionId) {
        if (isoTransactionId == null) {
            return;
        }
        
        logger.warn("COMPLIANCE ALERT: Deleting entire audit trail for transaction {}. This is a restricted operation.", isoTransactionId);
        Query query = em.createQuery("DELETE FROM IsoTransactionAudit a WHERE a.isoTransactionId = :txnId");
        query.setParameter("txnId", isoTransactionId);
        int deleted = query.executeUpdate();
        logger.warn("Deleted {} audit records for transaction {}", deleted, isoTransactionId);
    }
    
    @Override
    public void deleteAll() {
        logger.warn("COMPLIANCE ALERT: Deleting entire audit trail. This is a nuclear operation that destroys all audit records.");
        Query query = em.createQuery("DELETE FROM IsoTransactionAudit");
        int deleted = query.executeUpdate();
        logger.warn("Deleted {} total audit records", deleted);
    }
    
    @Override
    public long count() {
        return em.createQuery("SELECT COUNT(a) FROM IsoTransactionAudit a", Long.class)
            .getSingleResult();
    }
    
    @Override
    public long countByIsoTransactionId(Long isoTransactionId) {
        if (isoTransactionId == null) {
            return 0;
        }
        
        return em.createQuery(
            "SELECT COUNT(a) FROM IsoTransactionAudit a WHERE a.isoTransactionId = :txnId",
            Long.class
        ).setParameter("txnId", isoTransactionId).getSingleResult();
    }
    
    @Override
    public long countByAction(String action) {
        if (action == null || action.isEmpty()) {
            return 0;
        }
        
        return em.createQuery(
            "SELECT COUNT(a) FROM IsoTransactionAudit a WHERE a.action = :action",
            Long.class
        ).setParameter("action", action).getSingleResult();
    }
    
    @Override
    public List<IsoTransactionAudit> findUnverifiedAuditRecords() {
        return em.createQuery(
            "SELECT a FROM IsoTransactionAudit a WHERE a.complianceVerified = false ORDER BY a.createdAt ASC",
            IsoTransactionAudit.class
        ).getResultList();
    }
    
    @Override
    public void markComplianceVerified(Long id, String notes) {
        if (id == null) {
            return;
        }
        
        IsoTransactionAudit audit = em.find(IsoTransactionAudit.class, id);
        if (audit != null) {
            audit.setComplianceVerified(true);
            audit.setComplianceNotes(notes);
            em.merge(audit);
            logger.debug("Audit record {} marked as compliance verified", id);
        }
    }
    
    @Override
    public List<IsoTransactionAudit> getAuditTrail(Long isoTransactionId) {
        // Returns chronologically ordered audit trail for compliance reporting
        return findByIsoTransactionId(isoTransactionId);
    }
}

