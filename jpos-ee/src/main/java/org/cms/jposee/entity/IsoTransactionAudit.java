package org.cms.jposee.entity;

import javax.persistence.*;
import java.time.LocalDateTime;

/**
 * JPA Entity: IsoTransactionAudit
 * 
 * Maps to the 'iso_transactions_audit' table in PostgreSQL
 * Tracks all changes to IsoTransaction records
 * PCI-DSS Requirement 10.3: Audit logs protected
 * Immutable audit trail for compliance verification
 * 
 * @author jPOS-EE Persistence Layer
 * @version 1.0
 * @since April 21, 2026
 */
@Entity
@Table(
    name = "iso_transactions_audit",
    schema = "public",
    indexes = {
        @Index(name = "idx_audit_txn_id", columnList = "iso_transaction_id"),
        @Index(name = "idx_audit_created_at", columnList = "created_at"),
        @Index(name = "idx_audit_action", columnList = "action")
    }
)
public class IsoTransactionAudit {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    // ================================================================
    // AUDIT TRANSACTION REFERENCE
    // ================================================================

    @Column(name = "iso_transaction_id", nullable = false)
    private Long isoTransactionId;  // Foreign key to iso_transactions.id

    // ================================================================
    // ACTION TRACKING (What changed?)
    // ================================================================

    @Column(name = "action", length = 50, nullable = false)
    private String action;  // CREATE, UPDATE, DELETE, STATUS_CHANGE

    // ================================================================
    // CHANGE DETAILS (Before/After values)
    // ================================================================

    @Column(name = "field_name", length = 100)
    private String fieldName;  // Which field changed

    @Column(name = "old_value", columnDefinition = "TEXT")
    private String oldValue;  // Previous value

    @Column(name = "new_value", columnDefinition = "TEXT")
    private String newValue;  // New value

    // ================================================================
    // USER & SESSION TRACKING (Who did it?)
    // ================================================================

    @Column(name = "changed_by", length = 100)
    private String changedBy;  // User who made the change

    @Column(name = "ip_address", length = 45)
    private String ipAddress;  // Client IP (IPv4 or IPv6)

    @Column(name = "session_id", length = 100)
    private String sessionId;  // Session ID for audit trail

    // ================================================================
    // REASON & NOTES
    // ================================================================

    @Column(name = "reason", columnDefinition = "TEXT")
    private String reason;  // Why the change was made

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;  // Additional notes

    // ================================================================
    // TIMESTAMP (When did it happen?)
    // ================================================================

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;  // Timestamp of the change

    // ================================================================
    // COMPLIANCE MARKERS
    // ================================================================

    @Column(name = "compliance_verified")
    private Boolean complianceVerified = false;  // Was compliance checked?

    @Column(name = "compliance_notes", columnDefinition = "TEXT")
    private String complianceNotes;  // Compliance check details

    // ================================================================
    // LIFECYCLE CALLBACKS
    // ================================================================

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        if (complianceVerified == null) {
            complianceVerified = false;
        }
    }

    // ================================================================
    // GETTERS & SETTERS
    // ================================================================

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getIsoTransactionId() {
        return isoTransactionId;
    }

    public void setIsoTransactionId(Long isoTransactionId) {
        this.isoTransactionId = isoTransactionId;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public String getFieldName() {
        return fieldName;
    }

    public void setFieldName(String fieldName) {
        this.fieldName = fieldName;
    }

    public String getOldValue() {
        return oldValue;
    }

    public void setOldValue(String oldValue) {
        this.oldValue = oldValue;
    }

    public String getNewValue() {
        return newValue;
    }

    public void setNewValue(String newValue) {
        this.newValue = newValue;
    }

    public String getChangedBy() {
        return changedBy;
    }

    public void setChangedBy(String changedBy) {
        this.changedBy = changedBy;
    }

    public String getIpAddress() {
        return ipAddress;
    }

    public void setIpAddress(String ipAddress) {
        this.ipAddress = ipAddress;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public Boolean getComplianceVerified() {
        return complianceVerified;
    }

    public void setComplianceVerified(Boolean complianceVerified) {
        this.complianceVerified = complianceVerified;
    }

    public String getComplianceNotes() {
        return complianceNotes;
    }

    public void setComplianceNotes(String complianceNotes) {
        this.complianceNotes = complianceNotes;
    }

    @Override
    public String toString() {
        return "IsoTransactionAudit{" +
                "id=" + id +
                ", isoTransactionId=" + isoTransactionId +
                ", action='" + action + '\'' +
                ", changedBy='" + changedBy + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
