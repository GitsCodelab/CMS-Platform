package org.cms.jposee.repository;

import org.cms.jposee.entity.IsoTransaction;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository interface for ISO Transaction persistence
 * Handles CRUD and query operations for iso_transactions table
 * 
 * Supports PCI-compliant transaction storage with audit trail
 * 
 * @author jPOS-EE Persistence Layer
 * @version 1.0
 * @since April 21, 2026
 */
public interface IsoTransactionRepository {
    
    // ============================================================
    // CREATE Operations
    // ============================================================
    
    /**
     * Persist a new ISO transaction record
     * Automatically sets timestamps and initializes audit fields
     * 
     * @param transaction the IsoTransaction entity to save
     * @return the saved transaction with generated ID
     */
    IsoTransaction save(IsoTransaction transaction);
    
    /**
     * Persist multiple transaction records in batch
     * Useful for high-volume transaction processing
     * 
     * @param transactions list of IsoTransaction entities
     * @return list of saved transactions with generated IDs
     */
    List<IsoTransaction> saveAll(List<IsoTransaction> transactions);
    
    // ============================================================
    // READ Operations
    // ============================================================
    
    /**
     * Find transaction by primary key (ID)
     * 
     * @param id the transaction ID (BIGSERIAL)
     * @return Optional containing transaction if found
     */
    Optional<IsoTransaction> findById(Long id);
    
    /**
     * Find transaction by STAN (unique system trace audit number)
     * Used to detect duplicate transactions and reversals
     * 
     * @param stan the 12-digit STAN
     * @return Optional containing transaction if found
     */
    Optional<IsoTransaction> findBySTAN(String stan);
    
    /**
     * Find transaction by RRN (retrieval reference number)
     * Used for transaction reconciliation and lookup
     * 
     * @param rrn the 12-digit RRN from response
     * @return Optional containing transaction if found
     */
    Optional<IsoTransaction> findByRRN(String rrn);
    
    /**
     * Find all transactions for a merchant
     * Used for settlement and reconciliation
     * 
     * @param merchantId the merchant identifier
     * @return list of merchant transactions
     */
    List<IsoTransaction> findByMerchantId(String merchantId);
    
    /**
     * Find all transactions for a terminal
     * Used for terminal reconciliation and monitoring
     * 
     * @param terminalId the terminal identifier
     * @return list of terminal transactions
     */
    List<IsoTransaction> findByTerminalId(String terminalId);
    
    /**
     * Find transactions by status
     * Used for transaction lifecycle monitoring (RECEIVED, PROCESSED, FAILED, DECLINED)
     * 
     * @param status the transaction status
     * @return list of transactions matching status
     */
    List<IsoTransaction> findByStatus(String status);
    
    /**
     * Find transactions within date range
     * Used for reporting, reconciliation, and compliance queries
     * 
     * @param startDate start of date range (inclusive)
     * @param endDate end of date range (inclusive)
     * @return list of transactions within range
     */
    List<IsoTransaction> findByDateRange(LocalDateTime startDate, LocalDateTime endDate);
    
    /**
     * Get all transactions (use with pagination for large datasets)
     * 
     * @return list of all transactions
     */
    List<IsoTransaction> findAll();
    
    /**
     * Check if transaction exists by STAN
     * 
     * @param stan the STAN to check
     * @return true if transaction with STAN exists
     */
    boolean existsBySTAN(String stan);
    
    // ============================================================
    // UPDATE Operations
    // ============================================================
    
    /**
     * Update an existing transaction
     * Automatically updates the updated_at timestamp
     * 
     * @param transaction the transaction with updated fields
     * @return the updated transaction
     */
    IsoTransaction update(IsoTransaction transaction);
    
    /**
     * Update transaction status
     * Common operation for marking transactions as PROCESSED, FAILED, DECLINED
     * 
     * @param id transaction ID
     * @param newStatus the new status value
     * @return the updated transaction
     */
    IsoTransaction updateStatus(Long id, String newStatus);
    
    /**
     * Mark transaction as processed with response data
     * Stores response code, auth ID, and raw response message
     * 
     * @param id transaction ID
     * @param responseCode the response code from processor
     * @param authIdResp the authorization ID if approved
     * @param rawResponse the complete raw response message (for audit trail)
     * @return the updated transaction
     */
    IsoTransaction updateWithResponse(Long id, String responseCode, String authIdResp, String rawResponse);
    
    /**
     * Increment retry count for failed transaction
     * Used for automatic retry logic
     * 
     * @param id transaction ID
     * @return the updated transaction
     */
    IsoTransaction incrementRetryCount(Long id);
    
    // ============================================================
    // DELETE Operations
    // ============================================================
    
    /**
     * Delete transaction by ID
     * NOTE: In production, use archive/soft-delete instead for audit compliance
     * 
     * @param id transaction ID
     */
    void deleteById(Long id);
    
    /**
     * Delete all transactions (use with caution!)
     * Typically only used in test environments
     */
    void deleteAll();
    
    // ============================================================
    // AGGREGATE Operations
    // ============================================================
    
    /**
     * Get total count of transactions
     * 
     * @return total number of transactions
     */
    long count();
    
    /**
     * Get count of transactions by status
     * Used for transaction monitoring and SLA tracking
     * 
     * @param status the status to count
     * @return count of transactions with that status
     */
    long countByStatus(String status);
    
    /**
     * Get sum of transaction amounts for date range
     * Used for settlement totaling and reconciliation
     * 
     * @param startDate start of period
     * @param endDate end of period
     * @return total transaction amount
     */
    java.math.BigDecimal sumAmountByDateRange(LocalDateTime startDate, LocalDateTime endDate);
    
    // ============================================================
    // COMPLIANCE Operations (PCI-DSS Requirement 10.3)
    // ============================================================
    
    /**
     * Find transactions not yet marked as compliance verified
     * Used for compliance audit logging
     * 
     * @return list of unverified transactions
     */
    List<IsoTransaction> findUnverifiedComplianceTransactions();
    
    /**
     * Mark transaction as compliance verified
     * Indicates audit trail has been reviewed and confirmed
     * 
     * @param id transaction ID
     */
    void markComplianceVerified(Long id);
}
