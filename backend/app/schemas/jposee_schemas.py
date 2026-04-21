"""Pydantic models/schemas for jPOS EE data structures"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    REVERSED = "reversed"


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    PURCHASE = "Purchase"
    REFUND = "Refund"
    TRANSFER = "Transfer"
    REVERSAL = "Reversal"
    INQUIRY = "Inquiry"
    BALANCE = "Balance"


class BatchJobStatus(str, Enum):
    """Batch job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionResult(str, Enum):
    """Audit log result enumeration"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"


class AlertLevel(str, Enum):
    """Alert level enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# TRANSACTION SCHEMAS
# ============================================================================

class TransactionCreate(BaseModel):
    """Schema for creating a new transaction"""
    txn_id: str = Field(..., description="Unique transaction ID")
    txn_type: str = Field(..., description="Transaction type")
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    status: str = Field(default="pending", description="Transaction status")
    card_last4: Optional[str] = Field(None, description="Last 4 digits of card")
    card_bin: Optional[str] = Field(None, description="Bank Identification Number")
    merchant_id: Optional[str] = Field(None, description="Merchant identifier")
    merchant_name: Optional[str] = Field(None, description="Merchant name")
    merchant_category: Optional[str] = Field(None, description="Merchant category code")
    iso_fields: Optional[Dict[str, Any]] = Field(None, description="ISO 8583 message fields")
    routing_info: Optional[Dict[str, Any]] = Field(None, description="Routing information")
    gateway_response: Optional[Dict[str, Any]] = Field(None, description="Gateway response")
    duration_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    retry_count: int = Field(default=0, description="Number of retries")


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction"""
    status: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    retry_count: Optional[int] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    txn_id: str
    txn_type: str
    amount: float
    currency: str
    status: str
    timestamp: datetime
    card_last4: Optional[str]
    card_bin: Optional[str]
    merchant_id: Optional[str]
    merchant_name: Optional[str]
    merchant_category: Optional[str]
    iso_fields: Optional[Dict[str, Any]]
    routing_info: Optional[Dict[str, Any]]
    gateway_response: Optional[Dict[str, Any]]
    duration_ms: Optional[int]
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for paginated transaction list"""
    total: int
    page: int
    limit: int
    transactions: List[TransactionResponse]


# ============================================================================
# ROUTING RULE SCHEMAS
# ============================================================================

class RoutingCriteria(BaseModel):
    """Schema for routing rule criteria"""
    message_type: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    bin_ranges: Optional[List[str]] = None
    merchant_category: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class RoutingAction(BaseModel):
    """Schema for routing rule action"""
    route: str = Field(..., description="Route/gateway name")
    transform_fields: Optional[Dict[str, Any]] = None
    log_level: str = Field(default="info", description="Logging level")
    timeout_ms: int = Field(default=5000, description="Timeout in milliseconds")


class RoutingRuleCreate(BaseModel):
    """Schema for creating a routing rule"""
    rule_name: str = Field(..., description="Unique rule name")
    rule_description: Optional[str] = None
    enabled: bool = Field(default=True)
    priority: int = Field(default=0)
    criteria: Dict[str, Any] = Field(..., description="Match criteria")
    action: Dict[str, Any] = Field(..., description="Action configuration")
    created_by: Optional[str] = None


class RoutingRuleUpdate(BaseModel):
    """Schema for updating a routing rule"""
    rule_name: Optional[str] = None
    rule_description: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None
    criteria: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None
    updated_by: Optional[str] = None


class RoutingRuleResponse(BaseModel):
    """Schema for routing rule response"""
    id: int
    rule_name: str
    rule_description: Optional[str]
    enabled: bool
    priority: int
    criteria: Dict[str, Any]
    action: Dict[str, Any]
    hit_count: int
    success_count: int
    failed_count: int
    total_duration_ms: int
    created_by: Optional[str]
    created_at: datetime
    updated_by: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


class RoutingRuleListResponse(BaseModel):
    """Schema for paginated routing rule list"""
    total: int
    page: int
    limit: int
    rules: List[RoutingRuleResponse]


class RouteTestRequest(BaseModel):
    """Schema for testing a route"""
    iso_message: Optional[str] = None
    amount: float
    card_bin: Optional[str] = None
    merchant_category: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class RouteTestResponse(BaseModel):
    """Schema for route test response"""
    matched_rule: Optional[str]
    route: str
    routing_info: Dict[str, Any]


# ============================================================================
# AUDIT LOG SCHEMAS
# ============================================================================

class AuditLogCreate(BaseModel):
    """Schema for creating an audit log"""
    action_type: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    result: str
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    action_type: str
    user_id: Optional[int]
    username: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    result: str
    error_message: Optional[str]
    details: Optional[Dict[str, Any]]
    changes: Optional[Dict[str, Any]]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list"""
    total: int
    page: int
    limit: int
    logs: List[AuditLogResponse]


# ============================================================================
# BATCH JOB SCHEMAS
# ============================================================================

class BatchJobCreate(BaseModel):
    """Schema for creating a batch job"""
    batch_name: str
    file_path: str
    file_type: str = Field(..., description="csv, xml, json")
    total_records: int
    mapping: Dict[str, Any]
    rules: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class BatchJobResponse(BaseModel):
    """Schema for batch job response"""
    id: int
    batch_id: str
    batch_name: str
    status: str
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    file_path: str
    file_type: str
    mapping: Dict[str, Any]
    rules: Optional[Dict[str, Any]]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BatchJobListResponse(BaseModel):
    """Schema for paginated batch job list"""
    total: int
    page: int
    limit: int
    jobs: List[BatchJobResponse]


class BatchResultResponse(BaseModel):
    """Schema for batch result"""
    id: int
    batch_id: int
    record_number: int
    txn_id: Optional[str]
    status: str
    error_message: Optional[str]
    input_data: Optional[Dict[str, Any]]
    processed_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class BatchResultsListResponse(BaseModel):
    """Schema for batch results list"""
    total: int
    page: int
    limit: int
    results: List[BatchResultResponse]


# ============================================================================
# ALERT SCHEMAS
# ============================================================================

class AlertHistoryResponse(BaseModel):
    """Schema for alert history"""
    id: int
    alert_level: str
    alert_message: str
    metric_name: Optional[str]
    threshold_value: Optional[float]
    actual_value: Optional[float]
    triggered_at: datetime
    resolved_at: Optional[datetime]
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertHistoryListResponse(BaseModel):
    """Schema for alert history list"""
    total: int
    page: int
    limit: int
    alerts: List[AlertHistoryResponse]


class AlertConfigResponse(BaseModel):
    """Schema for alert configuration"""
    config_key: str
    config_value: str
    description: Optional[str]


# ============================================================================
# MONITORING SCHEMAS
# ============================================================================

class MetricsSnapshot(BaseModel):
    """Schema for metrics snapshot"""
    transactions_per_sec: float
    error_rate_percent: float
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_mbps: float
    active_transactions: int
    queue_depth: int
    metric_time: datetime


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics"""
    total_transactions: int
    successful_transactions: int
    failed_transactions: int
    success_rate_percent: Optional[float] = None
    avg_response_time_ms: Optional[float] = None
    last_transaction_timestamp: Optional[datetime] = None
    transactions_today: int
    system_health: str
    last_sync_time: Optional[datetime] = None


class SystemHealthResponse(BaseModel):
    """Schema for system health"""
    jposee_status: str
    database_status: str
    database_version: str
    api_status: str
    last_transaction: Optional[datetime]
    uptime_seconds: int
    version: str


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class RoutingAnalyticsResponse(BaseModel):
    """Schema for routing analytics"""
    id: int
    rule_name: str
    hit_count: int
    success_count: int
    failed_count: int
    success_rate_percent: Optional[float] = None
    avg_processing_ms: Optional[float] = None


class RoutingAnalyticsListResponse(BaseModel):
    """Schema for routing analytics list"""
    total_rules: int
    analytics: List[RoutingAnalyticsResponse]


# ============================================================================
# FILTER SCHEMAS
# ============================================================================

class TransactionFilterParams(BaseModel):
    """Schema for transaction filtering"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    status: Optional[str] = None
    txn_type: Optional[str] = None
    merchant_id: Optional[str] = None
    card_bin: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    search: Optional[str] = None


class AuditLogFilterParams(BaseModel):
    """Schema for audit log filtering"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    action_type: Optional[str] = None
    user_id: Optional[int] = None
    resource_type: Optional[str] = None
    result: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[str] = None
