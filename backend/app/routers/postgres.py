"""PostgreSQL database routes"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from app.schemas import TestRecordCreate, TestRecordResponse, TestRecordUpdate
from app.database import postgres_db

router = APIRouter(prefix="/postgres", tags=["PostgreSQL"])


@router.get("/test", response_model=List[Dict[str, Any]])
async def get_all_records():
    """Get all records from PostgreSQL test table"""
    try:
        records = postgres_db.get_all("test")
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL error: {str(e)}"
        )


@router.get("/test/{record_id}", response_model=Optional[Dict[str, Any]])
async def get_record_by_id(record_id: int):
    """Get a single record from PostgreSQL test table by ID"""
    try:
        record = postgres_db.get_by_id("test", record_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record with ID {record_id} not found"
            )
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL error: {str(e)}"
        )


@router.post("/test", status_code=status.HTTP_201_CREATED)
async def create_record(record: TestRecordCreate):
    """Create a new record in PostgreSQL test table"""
    try:
        data = {k: v for k, v in record.dict().items() if v is not None and k != "id"}
        result = postgres_db.create("test", data)
        return {
            "status": "success",
            "message": "Record created successfully in PostgreSQL",
            "affected_rows": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL error: {str(e)}"
        )


@router.put("/test/{record_id}")
async def update_record(record_id: int, record: TestRecordUpdate):
    """Update a record in PostgreSQL test table"""
    try:
        data = {k: v for k, v in record.dict().items() if v is not None}
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update"
            )
        result = postgres_db.update("test", record_id, data)
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record with ID {record_id} not found"
            )
        return {
            "status": "success",
            "message": "Record updated successfully in PostgreSQL",
            "affected_rows": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL error: {str(e)}"
        )


@router.delete("/test/{record_id}")
async def delete_record(record_id: int):
    """Delete a record from PostgreSQL test table"""
    try:
        result = postgres_db.delete("test", record_id)
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record with ID {record_id} not found"
            )
        return {
            "status": "success",
            "message": "Record deleted successfully from PostgreSQL",
            "affected_rows": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL error: {str(e)}"
        )
