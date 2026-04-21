package org.cms.jposee.repository;

import org.cms.jposee.entity.IsoTransactionAudit;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * Repository interface for ISO Transaction Audit Trail
 * Handles CRUD operations for iso_transactions_audit table
 * 
 * Maintains immutable audit trail for PCI-DSS compliance (Requirement 10.3)
 * All audit records are created once and never modified or deleted
 * 
 * @author jPOS-EE Persistence Layer
 * @version 1.0
 * @since April 21, 2026
 */
public interface IsoTransactionAuditRepository {
    
    // ============================================================
    // CREATE Operations (Only operation supported)
    // ============================================================
    
    /**
     * Create new audit record for transaction change
     * Audit records are IMMUTABLE - once created, never modified
     * 
     * @param auditRecord the audit entry to record
     * @return the created audit record with generated ID
     */
    IsoTransactionAudit save(IsoTransactionAudit auditRecord);
    
    /**
     * Create multiple audit records (batch insert)
     * Used for transaction state changes involving multiple fields
     * 
     * @param auditRecords list of audit entries
     * @return list of created audit records with generated IDs
     */
    List<IsoTransactionAudit> saveAll(List<IsoTransactionAudit> auditRecords);
    
    // ============================================================
    // READ Operations
    // ============================================================
    
    /**
     * Find audit record by ID
     * 
     * @param id the audit record ID
     * @return Optional containing audit record if found
     */
    Optional<IsoTransactionAudit> findById(Long id);
    
    /**
     * Find all audit records for a transaction
     * Provides complete change history for a transaction
     * Critical for PCI-DSS Requirement 10.3 audit trails
     * 
     * @param isoTransactionId the transaction ID
     * @return list of audit records in chronological order
     */
    List<IsoTransactionAudit> findByIsoTransactionId(Long isoTransactionId);
    
    /**
     * Find audit records by action type
     * Used to find specific changes (CREATE, UPDATE, DELETE, STATUS_CHANGE)
     * 
     * @param action the action type to filter
     * @return list of audit records matching action
     */
    List<IsoTransactionAudit> findByAction(String action);
    
    /**
     * Find audit records within date range
     * Used for compliance reporting and historical analysis
     * 
     * @param startDate start of date range
     * @param endDate end of date range
     * @return list of audit records within range
     */
    List<IsoTransactionAudit> findByDateRange(LocalDateTime startDate, LocalDateTime endDate);
    
    /**
     * Find audit records by user (changed_by field)
     * Used to identify which user/system made changes
     * 
     * @param changedBy the user/system identifier
     * @return list of audit records created by that user/system
     */
    List<IsoTransactionAudit> findByChangedBy(String changedBy);
    
    /**
     * Find audit records by IP address
     * Used for security auditing - trace where changes came from
     * 
     * @param ipAddress the source IP address
     * @return list of audit records from that IP
     */
    List<IsoTransactionAudit> findByIpAddress(String ipAddress);
    
    /**
     * Find audit records by session ID
     * Used to group changes by user session
     * 
     * @param sessionId the jPOS session ID
     * @return list of audit records in that session
     */
    List<IsoTransactionAudit> findBySessionId(String sessionId);
    
    /**
     * Find audit records for specific field changes
     * Useful for tracking specific data modifications
     * 
     * @param fieldName the field that was changed
     * @return list of audit records for that field
     */
    List<IsoTransactionAudit> findByFieldName(String fieldName);
    
    /**
     * Get all audit records (use with pagination)
     * 
     * @return list of all audit records
     */
    List<IsoTransactionAudit> findAll();
    
    // ============================================================
    // DELETE Operations (Restricted in production)
    // ============================================================
    
    /**
     * Delete audit record by ID
     * WARNING: Violates PCI-DSS Requirement 10.3
     * Should NEVER be used in production environments
     * Only use in test/development scenarios
     * 
     * @param id the audit record ID
     */
    void deleteById(Long id);
    
    /**
     * Delete all audit records for a transaction
     * WARNING: Violates audit trail requirements
     * Should NEVER be used in production
     * 
     * @param isoTransactionId the transaction ID
     */
    void deleteByIsoTransactionId(Long isoTransactionId);
    
    /**
     * Delete all audit records
     * WARNING: This is a nuclear option - destroys entire audit trail
     * Should NEVER be called in production
     * Only use in test environment resets
     */
    void deleteAll();
    
    // ============================================================
    // AGGREGATE Operations
    // ============================================================
    
    /**
     * Get total count of audit records
     * Used for audit trail size monitoring
     * 
     * @return total number of audit records
     */
    long count();
    
    /**
     * Get count of audit records for transaction
     * Shows how many changes have been made to a transaction
     * 
     * @param isoTransactionId the transaction ID
     * @return count of audit entries for that transaction
     */
    long countByIsoTransactionId(Long isoTransactionId);
    
    /**
     * Get count of audit records by action type
     * Used for compliance statistics (how many creates, updates, etc)
     * 
     * @param action the action type
     * @return count of audit records with that action
     */
    long countByAction(String action);
    
    // ============================================================
    // COMPLIANCE Operations (PCI-DSS Requirement 10.3)
    // ============================================================
    
    /**
     * Find unverified audit records
     * Used to identify audit entries not yet reviewed for compliance
     * 
     * @return list of audit records with compliance_verified = false
     */
    List<IsoTransactionAudit> findUnverifiedAuditRecords();
    
    /**
     * Mark audit record as compliance verified
     * Indicates audit entry has been reviewed and confirmed
     * 
     * @param id the audit record ID
     * @param notes compliance review notes
     */
    void markComplianceVerified(Long id, String notes);
    
    /**
     * Get audit trail for transaction in chronological order
     * Returns audit history suitable for compliance reporting
     * 
     * @param isoTransactionId the transaction ID
     * @return chronologically ordered audit records
     */
    List<IsoTransactionAudit> getAuditTrail(Long isoTransactionId);
}
