from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from config import settings
from oracle_db import oracle_db
from postgres_db import postgres_db

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Dual-database CRUD API for Oracle XE and PostgreSQL"
)

# Pydantic models for request/response
class TestRecord(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api": settings.API_TITLE,
        "version": settings.API_VERSION
    }

# Oracle Database Endpoints
@app.get("/oracle/test", tags=["Oracle"], response_model=List[Dict[str, Any]])
async def get_oracle_test_all():
    """Get all records from Oracle test table"""
    try:
        records = oracle_db.get_all("test")
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oracle error: {str(e)}"
        )

@app.get("/oracle/test/{record_id}", tags=["Oracle"], response_model=Optional[Dict[str, Any]])
async def get_oracle_test_by_id(record_id: int):
    """Get a single record from Oracle test table by ID"""
    try:
        record = oracle_db.get_by_id("test", record_id)
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
            detail=f"Oracle error: {str(e)}"
        )

@app.post("/oracle/test", tags=["Oracle"], status_code=status.HTTP_201_CREATED)
async def create_oracle_test(record: TestRecord):
    """Create a new record in Oracle test table"""
    try:
        # Include all non-None values, including ID if provided
        data = {k: v for k, v in record.dict().items() if v is not None}
        result = oracle_db.create("test", data)
        return {
            "status": "success",
            "message": "Record created successfully in Oracle",
            "affected_rows": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oracle error: {str(e)}"
        )

@app.put("/oracle/test/{record_id}", tags=["Oracle"])
async def update_oracle_test(record_id: int, record: TestRecord):
    """Update a record in Oracle test table"""
    try:
        data = {k: v for k, v in record.dict().items() if v is not None and k != "id"}
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data provided for update"
            )
        result = oracle_db.update("test", record_id, data)
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record with ID {record_id} not found"
            )
        return {
            "status": "success",
            "message": "Record updated successfully in Oracle",
            "affected_rows": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oracle error: {str(e)}"
        )

@app.delete("/oracle/test/{record_id}", tags=["Oracle"])
async def delete_oracle_test(record_id: int):
    """Delete a record from Oracle test table"""
    try:
        result = oracle_db.delete("test", record_id)
        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Record with ID {record_id} not found"
            )
        return {
            "status": "success",
            "message": "Record deleted successfully from Oracle",
            "affected_rows": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oracle error: {str(e)}"
        )

# PostgreSQL Database Endpoints
@app.get("/postgres/test", tags=["PostgreSQL"], response_model=List[Dict[str, Any]])
async def get_postgres_test_all():
    """Get all records from PostgreSQL test table"""
    try:
        records = postgres_db.get_all("test")
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL error: {str(e)}"
        )

@app.get("/postgres/test/{record_id}", tags=["PostgreSQL"], response_model=Optional[Dict[str, Any]])
async def get_postgres_test_by_id(record_id: int):
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

@app.post("/postgres/test", tags=["PostgreSQL"], status_code=status.HTTP_201_CREATED)
async def create_postgres_test(record: TestRecord):
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

@app.put("/postgres/test/{record_id}", tags=["PostgreSQL"])
async def update_postgres_test(record_id: int, record: TestRecord):
    """Update a record in PostgreSQL test table"""
    try:
        data = {k: v for k, v in record.dict().items() if v is not None and k != "id"}
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

@app.delete("/postgres/test/{record_id}", tags=["PostgreSQL"])
async def delete_postgres_test(record_id: int):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
