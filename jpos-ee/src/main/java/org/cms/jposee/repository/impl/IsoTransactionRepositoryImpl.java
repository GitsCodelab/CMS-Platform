package org.cms.jposee.repository.impl;

import org.cms.jposee.entity.IsoTransaction;
import org.cms.jposee.repository.IsoTransactionRepository;
import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.TypedQuery;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * JPA Implementation of IsoTransactionRepository
 * Uses EntityManager for all persistence operations
 * 
 * @author jPOS-EE Persistence Layer
 * @version 1.0
 * @since April 21, 2026
 */
public class IsoTransactionRepositoryImpl implements IsoTransactionRepository {
    
    @PersistenceContext(unitName = "jposee-persistence")
    private EntityManager em;
    
    public IsoTransactionRepositoryImpl(EntityManager entityManager) {
        this.em = entityManager;
    }
    
    // ============================================================
    // CREATE Operations
    // ============================================================
    
    @Override
    public IsoTransaction save(IsoTransaction transaction) {
        if (transaction.getId() == null) {
            em.persist(transaction);
            return transaction;
        } else {
            return em.merge(transaction);
        }
    }
    
    @Override
    public List<IsoTransaction> saveAll(List<IsoTransaction> transactions) {
        for (int i = 0; i < transactions.size(); i++) {
            IsoTransaction txn = transactions.get(i);
            if (txn.getId() == null) {
                em.persist(txn);
            } else {
                em.merge(txn);
            }
            
            // Batch flush every 20 records for performance
            if ((i + 1) % 20 == 0) {
                em.flush();
                em.clear();
            }
        }
        em.flush();
        return transactions;
    }
    
    // ============================================================
    // READ Operations
    // ============================================================
    
    @Override
    public Optional<IsoTransaction> findById(Long id) {
        IsoTransaction txn = em.find(IsoTransaction.class, id);
        return Optional.ofNullable(txn);
    }
    
    @Override
    public Optional<IsoTransaction> findBySTAN(String stan) {
        TypedQuery<IsoTransaction> query = em.createQuery(
            "SELECT t FROM IsoTransaction t WHERE t.stan = :stan",
            IsoTransaction.class
        );
        query.setParameter("stan", stan);
        try {
            return Optional.of(query.getSingleResult());
        } catch (javax.persistence.NoResultException e) {
            return Optional.empty();
        }
    }
    
    @Override
    public Optional<IsoTransaction> findByRRN(String rrn) {
        TypedQuery<IsoTransaction> query = em.createQuery(
            "SELECT t FROM IsoTransaction t WHERE t.rrn = :rrn",
            IsoTransaction.class
        );
        query.setParameter("rrn", rrn);
        try {
            return Optional.of(query.getSingleResult());
        } catch (javax.persistence.NoResultException e) {
            return Optional.empty();
        }
    }
    
    @Override
    public List<IsoTransaction> findByMerchantId(String merchantId) {
        TypedQuery<IsoTransaction> query = em.createQuery(
            "SELECT t FROM IsoTransaction t WHERE t.merchantId = :merchantId ORDER BY t.createdAt DESC",
            IsoTransaction.class
        );
        query.setParameter("merchantId", merchantId);
        return query.getResultList();
    }
    
    @Override
    public List<IsoTransaction> findByTerminalId(String terminalId) {
        TypedQuery<IsoTransaction> query = em.createQuery(
            "SELECT t FROM IsoTransaction t WHERE t.terminalId = :terminalId ORDER BY t.createdAt DESC",
            IsoTransaction.class
        );
        query.setParameter("terminalId", terminalId);
        return query.getResultList();
    }
    
    @Override
    public List<IsoTransaction> findByStatus(String status) {
        TypedQuery<IsoTransaction> query = em.createQuery(
            "SELECT t FROM IsoTransaction t WHERE t.status = :status ORDER BY t.createdAt DESC",
            IsoTransaction.class
        );
        query.setParameter("status", status);
        return query.getResultList();
    }
    
    @Override
    public List<IsoTransaction> findByDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        TypedQuery<IsoTransaction> query = em.createQuery(
            "SELECT t FROM IsoTransaction t WHERE t.createdAt BETWEEN :startDate AND :endDate ORDER BY t.createdAt DESC",
            IsoTransaction.class
        );
        query.setParameter("startDate", startDate);
        query.setParameter("endDate", endDate);
        return query.getResultList();
    }
    
    @Override
    public List<IsoTransaction> findAll() {
        TypedQuery<IsoTransaction> query = em.createQuery(
            "SELECT t FROM IsoTransaction t ORDER BY t.createdAt DESC",
            IsoTransaction.class
        );
        return query.getResultList();
    }
    
    @Override
    public boolean existsBySTAN(String stan) {
        TypedQuery<Long> query = em.createQuery(
            "SELECT COUNT(t) FROM IsoTransaction t WHERE t.stan = :stan",
            Long.class
        );
        query.setParameter("stan", stan);
        return query.getSingleResult() > 0;
    }
    
    // ============================================================
    // UPDATE Operations
    // ============================================================
    
    @Override
    public IsoTransaction update(IsoTransaction transaction) {
        transaction.setUpdatedAt(LocalDateTime.now());
        return em.merge(transaction);
    }
    
    @Override
    public IsoTransaction updateStatus(Long id, String newStatus) {
        IsoTransaction txn = em.find(IsoTransaction.class, id);
        if (txn != null) {
            txn.setStatus(newStatus);
            txn.setUpdatedAt(LocalDateTime.now());
            return em.merge(txn);
        }
        return null;
    }
    
    @Override
    public IsoTransaction updateWithResponse(Long id, String responseCode, String authIdResp, String rawResponse) {
        IsoTransaction txn = em.find(IsoTransaction.class, id);
        if (txn != null) {
            txn.setResponseCode(responseCode);
            txn.setAuthIdResp(authIdResp);
            txn.setRawResponse(rawResponse);
            txn.setStatus("PROCESSED");
            txn.setUpdatedAt(LocalDateTime.now());
            return em.merge(txn);
        }
        return null;
    }
    
    @Override
    public IsoTransaction incrementRetryCount(Long id) {
        IsoTransaction txn = em.find(IsoTransaction.class, id);
        if (txn != null) {
            int currentRetries = txn.getRetryCount() != null ? txn.getRetryCount() : 0;
            txn.setRetryCount(currentRetries + 1);
            txn.setUpdatedAt(LocalDateTime.now());
            return em.merge(txn);
        }
        return null;
    }
    
    // ============================================================
    // DELETE Operations
    // ============================================================
    
    @Override
    public void deleteById(Long id) {
        IsoTransaction txn = em.find(IsoTransaction.class, id);
        if (txn != null) {
            em.remove(txn);
        }
    }
    
    @Override
    public void deleteAll() {
        em.createQuery("DELETE FROM IsoTransaction").executeUpdate();
    }
    
    // ============================================================
    // AGGREGATE Operations
    // ============================================================
    
    @Override
    public long count() {
        return em.createQuery("SELECT COUNT(t) FROM IsoTransaction t", Long.class)
            .getSingleResult();
    }
    
    @Override
    public long countByStatus(String status) {
        return em.createQuery(
            "SELECT COUNT(t) FROM IsoTransaction t WHERE t.status = :status",
            Long.class
        ).setParameter("status", status).getSingleResult();
    }
    
    @Override
    public BigDecimal sumAmountByDateRange(LocalDateTime startDate, LocalDateTime endDate) {
        BigDecimal result = em.createQuery(
            "SELECT SUM(t.amount) FROM IsoTransaction t WHERE t.createdAt BETWEEN :startDate AND :endDate",
            BigDecimal.class
        )
        .setParameter("startDate", startDate)
        .setParameter("endDate", endDate)
        .getSingleResult();
        return result != null ? result : BigDecimal.ZERO;
    }
    
    // ============================================================
    // COMPLIANCE Operations
    // ============================================================
    
    @Override
    public List<IsoTransaction> findUnverifiedComplianceTransactions() {
        return em.createQuery(
            "SELECT t FROM IsoTransaction t WHERE t.complianceChecked = false ORDER BY t.createdAt ASC",
            IsoTransaction.class
        ).getResultList();
    }
    
    @Override
    public void markComplianceVerified(Long id) {
        IsoTransaction txn = em.find(IsoTransaction.class, id);
        if (txn != null) {
            txn.setComplianceChecked(true);
            txn.setUpdatedAt(LocalDateTime.now());
            em.merge(txn);
        }
    }
}
