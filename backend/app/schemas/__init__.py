"""Request/Response schemas for test table"""
from typing import Optional
from pydantic import BaseModel

# Import jPOS EE schemas
from app.schemas.jposee_schemas import (
    TransactionCreate, TransactionResponse, TransactionListResponse,
    TransactionUpdate, TransactionFilterParams,
    RoutingRuleCreate, RoutingRuleResponse, RoutingRuleListResponse,
    RoutingRuleUpdate, RouteTestRequest, RouteTestResponse,
    RoutingAnalyticsResponse, RoutingAnalyticsListResponse,
    AuditLogCreate, AuditLogResponse, AuditLogListResponse,
    AuditLogFilterParams,
    BatchJobCreate, BatchJobResponse, BatchJobListResponse,
    AlertHistoryResponse, AlertHistoryListResponse, AlertConfigResponse,
    MetricsSnapshot, DashboardStatsResponse, SystemHealthResponse,
    RoutingCriteria, RoutingAction,
    TransactionStatus, TransactionType, BatchJobStatus, ActionResult, AlertLevel
)


class TestRecordBase(BaseModel):
    """Base schema for test records"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TestRecordCreate(TestRecordBase):
    """Schema for creating test records"""
    id: Optional[int] = None


class TestRecordUpdate(TestRecordBase):
    """Schema for updating test records"""
    pass


class TestRecordResponse(TestRecordBase):
    """Schema for test record response"""
    id: int

    class Config:
        from_attributes = True


__all__ = [
    "TestRecordBase", "TestRecordCreate", "TestRecordUpdate", "TestRecordResponse",
    # jPOS EE schemas
    "TransactionCreate", "TransactionResponse", "TransactionListResponse", "TransactionUpdate",
    "RoutingRuleCreate", "RoutingRuleResponse", "RoutingRuleListResponse", "RoutingRuleUpdate",
    "RouteTestRequest", "RouteTestResponse", "RoutingAnalyticsResponse", "RoutingAnalyticsListResponse",
    "AuditLogCreate", "AuditLogResponse", "AuditLogListResponse",
    "BatchJobCreate", "BatchJobResponse", "BatchJobListResponse",
    "AlertHistoryResponse", "AlertHistoryListResponse", "AlertConfigResponse",
    "MetricsSnapshot", "DashboardStatsResponse", "SystemHealthResponse",
    "RoutingCriteria", "RoutingAction",
    "TransactionStatus", "TransactionType", "BatchJobStatus", "ActionResult", "AlertLevel"
]


class TestRecordResponse(TestRecordBase):
    """Schema for test record responses"""
    id: Optional[int] = None

    class Config:
        from_attributes = True


class APIResponse(BaseModel):
    """Standard API response schema"""
    status: str
    message: str
    data: Optional[dict] = None
    affected_rows: Optional[int] = None
