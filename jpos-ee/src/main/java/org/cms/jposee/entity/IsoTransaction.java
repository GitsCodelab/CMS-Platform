package org.cms.jposee.entity;

import javax.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * JPA Entity: IsoTransaction
 * 
 * Maps to the 'iso_transactions' table in PostgreSQL
 * Stores complete ISO 8583 transaction data including raw request/response
 * PCI-DSS compliant with comprehensive audit trail
 * 
 * @author jPOS-EE Persistence Layer
 * @version 1.0
 * @since April 21, 2026
 */
@Entity
@Table(
    name = "iso_transactions",
    schema = "public",
    indexes = {
        @Index(name = "idx_stan", columnList = "stan", unique = true),
        @Index(name = "idx_rrn", columnList = "rrn"),
        @Index(name = "idx_pan_masked", columnList = "pan_masked"),
        @Index(name = "idx_merchant_id", columnList = "merchant_id"),
        @Index(name = "idx_terminal_id", columnList = "terminal_id"),
        @Index(name = "idx_created_at", columnList = "created_at"),
        @Index(name = "idx_status", columnList = "status"),
        @Index(name = "idx_mti", columnList = "mti"),
        @Index(name = "idx_created_status", columnList = "created_at,status")
    }
)
public class IsoTransaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    // ================================================================
    // ISO 8583 CORE FIELDS (Parsed from message)
    // ================================================================

    @Column(name = "mti", length = 4, nullable = false)
    private String mti;  // Message Type Indicator (0100, 0200, 0400, etc.)

    @Column(name = "pan", length = 19)
    private String pan;  // Primary Account Number (MASKED in DB)

    @Column(name = "pan_masked", length = 19)
    private String panMasked;  // PAN masked: XXXXXX****1234

    @Column(name = "processing_code", length = 6)
    private String processingCode;  // Transaction type (000000=purchase, etc.)

    @Column(name = "amount", precision = 15, scale = 2, nullable = false)
    private BigDecimal amount;  // Transaction amount

    @Column(name = "currency_code", length = 3)
    private String currencyCode;  // ISO 4217 currency code (840=USD, etc.)

    @Column(name = "stan", length = 12, nullable = false, unique = true)
    private String stan;  // System Trace Audit Number (must be unique)

    @Column(name = "rrn", length = 12)
    private String rrn;  // Retrieval Reference Number

    // ================================================================
    // RESPONSE FIELDS
    // ================================================================

    @Column(name = "response_code", length = 2)
    private String responseCode;  // Field 39: Response code (00=approved, etc.)

    @Column(name = "auth_id_resp", length = 6)
    private String authIdResp;  // Authorization ID Response (Field 38)

    // ================================================================
    // RAW ISO MESSAGES (CRITICAL FOR PCI COMPLIANCE - IMMUTABLE)
    // ================================================================

    @Column(name = "raw_request", columnDefinition = "TEXT", nullable = false)
    private String rawRequest;  // Complete ISO request (base64 or hex encoded)

    @Column(name = "raw_response", columnDefinition = "TEXT")
    private String rawResponse;  // Complete ISO response (base64 or hex encoded)

    // ================================================================
    // MERCHANT & TERMINAL INFO
    // ================================================================

    @Column(name = "merchant_id", length = 15)
    private String merchantId;  // Field 42: Merchant ID

    @Column(name = "terminal_id", length = 8)
    private String terminalId;  // Field 41: Terminal ID

    @Column(name = "merchant_name", length = 100)
    private String merchantName;  // Merchant name (from Field 59)

    // ================================================================
    // PROCESSING STATUS & ERRORS
    // ================================================================

    @Column(name = "status", length = 20, nullable = false)
    private String status;  // RECEIVED|PROCESSED|FAILED|DECLINED

    @Column(name = "error_message", columnDefinition = "TEXT")
    private String errorMessage;  // Error details if failed

    @Column(name = "retry_count", columnDefinition = "INTEGER DEFAULT 0")
    private Integer retryCount = 0;  // Number of retry attempts

    // ================================================================
    // PCI-DSS COMPLIANCE FIELDS
    // ================================================================

    @Column(name = "sensitive_data_encrypted")
    private Boolean sensitiveDataEncrypted = false;  // PAN encrypted flag

    @Column(name = "compliance_checked")
    private Boolean complianceChecked = false;  // Compliance verification flag

    @Column(name = "ip_address", length = 45)
    private String ipAddress;  // Client IP for audit (IPv4 or IPv6)

    @Column(name = "session_id", length = 100)
    private String sessionId;  // Session ID for audit trail

    // ================================================================
    // AUDIT FIELDS (Automatic timestamps)
    // ================================================================

    @Column(name = "created_by", length = 100)
    private String createdBy;  // User who created the record

    @Column(name = "updated_by", length = 100)
    private String updatedBy;  // User who last updated the record

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;  // Creation timestamp

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;  // Last update timestamp

    // ================================================================
    // LIFECYCLE CALLBACKS
    // ================================================================

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
        if (retryCount == null) {
            retryCount = 0;
        }
        if (sensitiveDataEncrypted == null) {
            sensitiveDataEncrypted = false;
        }
        if (complianceChecked == null) {
            complianceChecked = false;
        }
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
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

    public String getMti() {
        return mti;
    }

    public void setMti(String mti) {
        this.mti = mti;
    }

    public String getPan() {
        return pan;
    }

    public void setPan(String pan) {
        this.pan = pan;
    }

    public String getPanMasked() {
        return panMasked;
    }

    public void setPanMasked(String panMasked) {
        this.panMasked = panMasked;
    }

    public String getProcessingCode() {
        return processingCode;
    }

    public void setProcessingCode(String processingCode) {
        this.processingCode = processingCode;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }

    public String getCurrencyCode() {
        return currencyCode;
    }

    public void setCurrencyCode(String currencyCode) {
        this.currencyCode = currencyCode;
    }

    public String getStan() {
        return stan;
    }

    public void setStan(String stan) {
        this.stan = stan;
    }

    public String getRrn() {
        return rrn;
    }

    public void setRrn(String rrn) {
        this.rrn = rrn;
    }

    public String getResponseCode() {
        return responseCode;
    }

    public void setResponseCode(String responseCode) {
        this.responseCode = responseCode;
    }

    public String getAuthIdResp() {
        return authIdResp;
    }

    public void setAuthIdResp(String authIdResp) {
        this.authIdResp = authIdResp;
    }

    public String getRawRequest() {
        return rawRequest;
    }

    public void setRawRequest(String rawRequest) {
        this.rawRequest = rawRequest;
    }

    public String getRawResponse() {
        return rawResponse;
    }

    public void setRawResponse(String rawResponse) {
        this.rawResponse = rawResponse;
    }

    public String getMerchantId() {
        return merchantId;
    }

    public void setMerchantId(String merchantId) {
        this.merchantId = merchantId;
    }

    public String getTerminalId() {
        return terminalId;
    }

    public void setTerminalId(String terminalId) {
        this.terminalId = terminalId;
    }

    public String getMerchantName() {
        return merchantName;
    }

    public void setMerchantName(String merchantName) {
        this.merchantName = merchantName;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Integer getRetryCount() {
        return retryCount;
    }

    public void setRetryCount(Integer retryCount) {
        this.retryCount = retryCount;
    }

    public Boolean getSensitiveDataEncrypted() {
        return sensitiveDataEncrypted;
    }

    public void setSensitiveDataEncrypted(Boolean sensitiveDataEncrypted) {
        this.sensitiveDataEncrypted = sensitiveDataEncrypted;
    }

    public Boolean getComplianceChecked() {
        return complianceChecked;
    }

    public void setComplianceChecked(Boolean complianceChecked) {
        this.complianceChecked = complianceChecked;
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

    public String getCreatedBy() {
        return createdBy;
    }

    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }

    public String getUpdatedBy() {
        return updatedBy;
    }

    public void setUpdatedBy(String updatedBy) {
        this.updatedBy = updatedBy;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    @Override
    public String toString() {
        return "IsoTransaction{" +
                "id=" + id +
                ", mti='" + mti + '\'' +
                ", stan='" + stan + '\'' +
                ", amount=" + amount +
                ", status='" + status + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
