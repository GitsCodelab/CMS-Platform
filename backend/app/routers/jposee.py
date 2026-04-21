"""jPOS EE API routes"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database.jposee import JposEEDB
from app.schemas.jposee_schemas import (
    TransactionCreate, TransactionResponse, TransactionListResponse,
    TransactionUpdate, TransactionFilterParams,
    RoutingRuleCreate, RoutingRuleResponse, RoutingRuleListResponse,
    RoutingRuleUpdate, RouteTestRequest, RouteTestResponse,
    RoutingAnalyticsResponse, RoutingAnalyticsListResponse,
    AuditLogCreate, AuditLogResponse, AuditLogListResponse,
    AuditLogFilterParams,
    BatchJobCreate, BatchJobResponse, BatchJobListResponse,
    AlertHistoryListResponse, AlertConfigResponse,
    DashboardStatsResponse, SystemHealthResponse
)

# Initialize router and database
router = APIRouter(prefix="/jposee", tags=["jPOS EE"])
jposee_db = JposEEDB()


# ============================================================================
# TRANSACTION ENDPOINTS
# ============================================================================

@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    txn_status: Optional[str] = Query(None, alias="status"),
    txn_type: Optional[str] = None,
    merchant_id: Optional[str] = None,
    card_bin: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    search: Optional[str] = None
):
    """Get paginated list of transactions with filtering"""
    try:
        filters = {
            'page': page,
            'limit': limit,
            'status': txn_status,
            'txn_type': txn_type,
            'merchant_id': merchant_id,
            'card_bin': card_bin,
            'date_from': date_from,
            'date_to': date_to,
            'amount_min': amount_min,
            'amount_max': amount_max,
            'search': search
        }
        
        transactions, total = jposee_db.list_transactions(filters)
        
        return TransactionListResponse(
            total=total,
            page=page,
            limit=limit,
            transactions=[TransactionResponse(**txn) for txn in transactions]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching transactions: {str(e)}"
        )


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int):
    """Get transaction details by ID"""
    try:
        transaction = jposee_db.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found"
            )
        return TransactionResponse(**transaction)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching transaction: {str(e)}"
        )


@router.post("/transactions", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate):
    """Create a new transaction"""
    try:
        txn_id = jposee_db.create_transaction(transaction.dict())
        return {
            "status": "success",
            "message": "Transaction created successfully",
            "transaction_id": txn_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating transaction: {str(e)}"
        )


@router.put("/transactions/{transaction_id}", response_model=Dict[str, Any])
async def update_transaction(transaction_id: int, transaction: TransactionUpdate):
    """Update a transaction"""
    try:
        rows_affected = jposee_db.update_transaction(
            transaction_id,
            transaction.dict(exclude_unset=True)
        )
        
        if rows_affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found"
            )
        
        return {
            "status": "success",
            "message": "Transaction updated successfully",
            "rows_affected": rows_affected
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating transaction: {str(e)}"
        )


@router.post("/transactions/{transaction_id}/retry", response_model=Dict[str, Any])
async def retry_transaction(transaction_id: int):
    """Retry a failed transaction"""
    try:
        # Get original transaction
        original_txn = jposee_db.get_transaction_by_id(transaction_id)
        if not original_txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found"
            )
        
        # Create new transaction with incremented retry count
        new_txn_data = original_txn.copy()
        new_txn_data['txn_id'] = f"{original_txn['txn_id']}_retry_{original_txn['retry_count'] + 1}"
        new_txn_data['status'] = 'pending'
        new_txn_data['retry_count'] = original_txn['retry_count'] + 1
        
        new_txn_id = jposee_db.create_transaction(new_txn_data)
        
        return {
            "status": "success",
            "message": "Transaction retry initiated",
            "original_transaction_id": transaction_id,
            "new_transaction_id": new_txn_id,
            "retry_count": new_txn_data['retry_count']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrying transaction: {str(e)}"
        )


# ============================================================================
# ROUTING RULE ENDPOINTS
# ============================================================================

@router.get("/routing/rules", response_model=RoutingRuleListResponse)
async def list_routing_rules(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    enabled: bool = Query(True)
):
    """Get paginated list of routing rules"""
    try:
        filters = {
            'page': page,
            'limit': limit,
            'enabled': enabled
        }
        
        rules, total = jposee_db.list_routing_rules(filters)
        
        return RoutingRuleListResponse(
            total=total,
            page=page,
            limit=limit,
            rules=[RoutingRuleResponse(**rule) for rule in rules]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching routing rules: {str(e)}"
        )


@router.get("/routing/rules/{rule_id}", response_model=RoutingRuleResponse)
async def get_routing_rule(rule_id: int):
    """Get routing rule details by ID"""
    try:
        rule = jposee_db.get_routing_rule(rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Routing rule with ID {rule_id} not found"
            )
        return RoutingRuleResponse(**rule)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching routing rule: {str(e)}"
        )


@router.post("/routing/rules", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_routing_rule(rule: RoutingRuleCreate):
    """Create a new routing rule"""
    try:
        rule_id = jposee_db.create_routing_rule(rule.dict())
        return {
            "status": "success",
            "message": "Routing rule created successfully",
            "rule_id": rule_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating routing rule: {str(e)}"
        )


@router.put("/routing/rules/{rule_id}", response_model=Dict[str, Any])
async def update_routing_rule(rule_id: int, rule: RoutingRuleUpdate):
    """Update a routing rule"""
    try:
        rows_affected = jposee_db.update_routing_rule(
            rule_id,
            rule.dict(exclude_unset=True)
        )
        
        if rows_affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Routing rule with ID {rule_id} not found"
            )
        
        return {
            "status": "success",
            "message": "Routing rule updated successfully",
            "rows_affected": rows_affected
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating routing rule: {str(e)}"
        )


@router.delete("/routing/rules/{rule_id}", response_model=Dict[str, Any])
async def delete_routing_rule(rule_id: int):
    """Delete a routing rule"""
    try:
        rows_affected = jposee_db.delete_routing_rule(rule_id)
        
        if rows_affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Routing rule with ID {rule_id} not found"
            )
        
        return {
            "status": "success",
            "message": "Routing rule deleted successfully",
            "rows_affected": rows_affected
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting routing rule: {str(e)}"
        )


@router.post("/routing/test", response_model=RouteTestResponse)
async def test_routing(request: RouteTestRequest):
    """Test message against routing rules"""
    try:
        # This is a simplified test - in production, integrate with actual jPOS
        rules, _ = jposee_db.list_routing_rules({'limit': 100})
        
        matched_rule = None
        for rule in rules:
            if rule.get('enabled'):
                # Simple matching logic - can be extended
                matched_rule = rule.get('rule_name')
                break
        
        return RouteTestResponse(
            matched_rule=matched_rule,
            route=matched_rule or "default_gateway",
            routing_info={
                "amount": request.amount,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing route: {str(e)}"
        )


@router.get("/routing/analytics", response_model=RoutingAnalyticsListResponse)
async def get_routing_analytics():
    """Get routing rules analytics"""
    try:
        analytics = jposee_db.get_routing_analytics()
        
        return RoutingAnalyticsListResponse(
            total_rules=len(analytics),
            analytics=[RoutingAnalyticsResponse(**item) for item in analytics]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching routing analytics: {str(e)}"
        )


# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@router.get("/audit/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    action_type: Optional[str] = None,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    result: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    """Get paginated list of audit logs"""
    try:
        filters = {
            'page': page,
            'limit': limit,
            'action_type': action_type,
            'user_id': user_id,
            'resource_type': resource_type,
            'result': result,
            'date_from': date_from,
            'date_to': date_to
        }
        
        logs, total = jposee_db.list_audit_logs(filters)
        
        return AuditLogListResponse(
            total=total,
            page=page,
            limit=limit,
            logs=[AuditLogResponse(**log) for log in logs]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching audit logs: {str(e)}"
        )


@router.post("/audit/logs", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_audit_log(log: AuditLogCreate):
    """Create an audit log entry"""
    try:
        log_id = jposee_db.create_audit_log(log.dict())
        return {
            "status": "success",
            "message": "Audit log created successfully",
            "log_id": log_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating audit log: {str(e)}"
        )


# ============================================================================
# BATCH JOB ENDPOINTS
# ============================================================================

@router.get("/batch/jobs", response_model=BatchJobListResponse)
async def list_batch_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None
):
    """Get paginated list of batch jobs"""
    try:
        filters = {
            'page': page,
            'limit': limit,
            'status': status
        }
        
        jobs, total = jposee_db.list_batch_jobs(filters)
        
        return BatchJobListResponse(
            total=total,
            page=page,
            limit=limit,
            jobs=[BatchJobResponse(**job) for job in jobs]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching batch jobs: {str(e)}"
        )


@router.get("/batch/jobs/{job_id}", response_model=BatchJobResponse)
async def get_batch_job(job_id: int):
    """Get batch job details by ID"""
    try:
        job = jposee_db.get_batch_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batch job with ID {job_id} not found"
            )
        return BatchJobResponse(**job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching batch job: {str(e)}"
        )


@router.post("/batch/jobs", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_batch_job(job: BatchJobCreate):
    """Create a new batch job"""
    try:
        job_id = jposee_db.create_batch_job(job.dict())
        return {
            "status": "success",
            "message": "Batch job created successfully",
            "job_id": job_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating batch job: {str(e)}"
        )


@router.put("/batch/jobs/{job_id}", response_model=Dict[str, Any])
async def update_batch_job(job_id: int, updates: Dict[str, Any]):
    """Update a batch job"""
    try:
        rows_affected = jposee_db.update_batch_job(job_id, updates)
        
        if rows_affected == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Batch job with ID {job_id} not found"
            )
        
        return {
            "status": "success",
            "message": "Batch job updated successfully",
            "rows_affected": rows_affected
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating batch job: {str(e)}"
        )


# ============================================================================
# MONITORING & DASHBOARD ENDPOINTS
# ============================================================================

@router.get("/monitoring/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = jposee_db.get_dashboard_stats()
        
        return DashboardStatsResponse(
            total_transactions=stats.get('total_transactions', 0),
            successful_transactions=stats.get('successful_transactions', 0),
            failed_transactions=stats.get('failed_transactions', 0),
            success_rate_percent=stats.get('success_rate_percent', 0),
            avg_response_time_ms=stats.get('avg_response_time_ms', 0),
            last_transaction_timestamp=stats.get('last_transaction_timestamp'),
            transactions_today=stats.get('total_transactions', 0),
            system_health="operational",
            last_sync_time=datetime.now()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard stats: {str(e)}"
        )


@router.get("/monitoring/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get system health status"""
    try:
        stats = jposee_db.get_dashboard_stats()
        
        return SystemHealthResponse(
            jposee_status="healthy",
            database_status="connected",
            database_version="1.0.0",
            api_status="operational",
            last_transaction=stats.get('last_transaction_timestamp'),
            uptime_seconds=3600,
            version="1.0.0"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching system health: {str(e)}"
        )
