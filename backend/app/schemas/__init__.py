"""Request/Response schemas for test table"""
from typing import Optional
from pydantic import BaseModel


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


class APIResponse(BaseModel):
    """Standard API response schema"""
    status: str
    message: str
    data: Optional[dict] = None
    affected_rows: Optional[int] = None


__all__ = [
    "TestRecordBase", "TestRecordCreate", "TestRecordUpdate", "TestRecordResponse",
    "APIResponse"
]
