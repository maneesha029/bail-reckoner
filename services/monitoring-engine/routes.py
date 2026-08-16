"""
API routes for Monitoring & Outreach Engine.

Three endpoints:
1. POST /api/v1/alerts/config — Save user notification preferences
2. GET /api/v1/alerts/pending — List pending alerts for user
3. GET /api/v1/alerts/scan — Internal trigger for scanner

Time Complexity: Route handlers are O(n) where n = number of alerts
Space Complexity: O(n) for storing query results
"""

from fastapi import FastAPI, HTTPException, Depends, Query, APIRouter
from requests import request
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import time
from typing import List, Optional
from schemas import StandardResponse

from config import config
from models import Alert, AlertConfig, AlertStatus, Base
from schemas import (
    AlertConfigRequest,
    AlertConfigResponse,
    AlertRecordResponse,
    PendingAlertsResponse,
    ScanResultResponse,
    StandardResponse,
    ErrorResponse,
)
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    config.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Test connection before use
)

SessionLocal = sessionmaker(bind=engine)

# ============================================================================
# App Setup
# ============================================================================

router = APIRouter()

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Monitoring & Outreach Engine for Bail Reckoner"
)

# ROUTE 1: Save Alert Config
@router.post("/api/v1/alerts/config")
async def save_alert_config(request: AlertConfigRequest):
    """Save or update alert configuration."""
    try:
        # Mock config object (replace with real DB in Phase 3)
        config_obj = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user_id": request.user_id,
            "email_enabled": request.email_enabled,
            "email_address": request.email_address,
            "sms_enabled": request.sms_enabled,
            "sms_number": request.sms_number,
            "notify_immediately": request.notify_immediately,
            "digest_enabled": request.digest_enabled,
            "digest_hour": request.digest_hour,
            "created_at": "2026-08-15T10:00:00Z"
        }
        
        return StandardResponse(
            success=True,
            data=config_obj,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ROUTE 2: Get Pending Alerts
@router.get("/api/v1/alerts/pending")
async def get_pending_alerts(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get pending alerts with optional filtering."""
    try:
        # Mock data (replace with real DB in Phase 3)
        pending_alerts = [
            {
                "alert_id": "alert-001",
                "case_id": "case-001",
                "prisoner_id": "PRIS-2026-00001",
                "state": "Maharashtra",
                "district": "Mumbai",
                "offense_category": "crimes_against_women",
                "max_sentence_months": 36,
                "custody_start_date": "2024-06-15T00:00:00Z",
                "eligibility_reason": "served_50_percent",
                "is_acknowledged": False,
                "created_at": "2026-08-15T10:00:00Z"
            },
            {
                "alert_id": "alert-002",
                "case_id": "case-002",
                "prisoner_id": "PRIS-2026-00002",
                "state": "Karnataka",
                "district": "Bengaluru",
                "offense_category": "economic_offences",
                "max_sentence_months": 84,
                "custody_start_date": "2023-12-01T00:00:00Z",
                "eligibility_reason": "served_50_percent",
                "is_acknowledged": False,
                "created_at": "2026-08-15T10:05:00Z"
            }
        ]
        
        return StandardResponse(
            success=True,
            data={
                "count": len(pending_alerts),
                "pending_alerts": pending_alerts,
                "filters_applied": {
                    "state": state,
                    "district": district,
                    "limit": limit,
                    "offset": offset
                }
            },
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ROUTE 3: Trigger Scan
@router.get("/api/v1/alerts/scan")
async def trigger_scan():
    """Manually trigger the case eligibility scan."""
    try:
        scan_result = {
            "scan_id": "scan-001",
            "total_cases_scanned": 150,
            "newly_eligible_found": 5,
            "new_alerts_created": 5,
            "already_flagged_skipped": 45,
            "errors": [],
            "scan_duration_seconds": 2.34,
            "timestamp": "2026-08-15T14:05:27Z"
        }
        
        return StandardResponse(
            success=True,
            data=scan_result,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ROUTE 4: Health Check
@router.get("/health")
async def health_check():
    return StandardResponse(
        success=True,
        data={"status": "healthy"},
        error=None
    )

@router.get("/")
async def root():
    return StandardResponse(
        success=True,
        data={"message": "Monitoring Engine API"},
        error=None
    )

# ============================================================================
# Database Dependency
# ============================================================================

def get_db() -> Session:
    """
    Dependency to get database session.
    
    In a real application, this would create a connection pool.
    For now, this is a placeholder that will be replaced with
    actual SQLAlchemy session management.
    
    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    # TODO: Replace with actual database session management
    # from sqlalchemy import create_engine
    # from sqlalchemy.orm import sessionmaker
    # engine = create_engine(config.DATABASE_URL)
    # SessionLocal = sessionmaker(bind=engine)
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    pass


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    
    Returns:
        Dict with status
    """
    return StandardResponse(
        success=True,
        data={"status": "healthy", "service": config.APP_NAME},
        error=None
    )


# ============================================================================
# Endpoint 1: POST /api/v1/alerts/config
# Save user notification preferences
# ============================================================================

@app.post("/api/v1/alerts/config")
def create_alert_config(request: AlertConfigRequest):
    mock_config = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": request.user_id,
        "email_enabled": request.email_enabled,
        "email_address": request.email_address,
        "sms_enabled": request.sms_enabled,
        "sms_number": request.sms_number,
        "notify_immediately": request.notify_immediately,
        "digest_enabled": request.digest_enabled,
        "digest_hour": request.digest_hour
    }  # ← Make sure this closing brace exists

# NEW (real database)
from sqlalchemy.orm import sessionmaker

def save_alert_config(request: AlertConfigRequest) -> StandardResponse:
    """Save alert configuration to database."""
    engine = create_engine(config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if already exists
        existing = db.query(AlertConfig).filter(
            AlertConfig.user_id == request.user_id
        ).first()
        
        if existing:
            # Update existing
            existing.email_enabled = request.email_enabled
            existing.email_address = request.email_address
            existing.sms_enabled = request.sms_enabled
            existing.sms_number = request.sms_number
            existing.notify_immediately = request.notify_immediately
            existing.digest_enabled = request.digest_enabled
            existing.digest_hour = request.digest_hour
            db.commit()
            db.refresh(existing)
            config_obj = existing
        else:
            # Create new
            config_obj = AlertConfig(
                user_id=request.user_id,
                email_enabled=request.email_enabled,
                email_address=request.email_address,
                sms_enabled=request.sms_enabled,
                sms_number=request.sms_number,
                notify_immediately=request.notify_immediately,
                digest_enabled=request.digest_enabled,
                digest_hour=request.digest_hour
            )
            db.add(config_obj)
            db.commit()
            db.refresh(config_obj)
        
        return StandardResponse(
            success=True,
            data=AlertConfigResponse.from_orm(config_obj).dict(),
            error=None
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()


# ============================================================================
# Endpoint 2: GET /api/v1/alerts/pending
# List pending alerts for a user or all alerts if admin
# ============================================================================

@app.get("/api/v1/alerts/pending")
# Replace mock data with real database query
def get_pending_alerts(
    state: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> StandardResponse:
    """Get pending alerts from database."""
    engine = create_engine(config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        query = db.query(Alert).filter(
            Alert.status == AlertStatus.PENDING.value
        )
        
        if state:
            query = query.filter(Alert.state == state)
        
        if district:
            query = query.filter(Alert.district == district)
        
        total_count = query.count()
        alerts = query.offset(offset).limit(limit).all()
        
        alert_responses = [
            AlertRecordResponse.from_orm(alert).dict()
            for alert in alerts
        ]
        
        return StandardResponse(
            success=True,
            data={
                "count": total_count,
                "pending_alerts": alert_responses,
                "filters_applied": {
                    "state": state,
                    "district": district,
                    "limit": limit,
                    "offset": offset
                }
            },
            error=None
        )
    
    finally:
        db.close()


# ============================================================================
# Endpoint 3: GET /api/v1/alerts/scan
# Internal endpoint to trigger scanner (called by scheduler or manually)
# ============================================================================

@app.get("/api/v1/alerts/scan")
def trigger_scan() -> StandardResponse:
    """
    Trigger the monitoring scanner to check for newly eligible cases.
    
    INTERNAL ENDPOINT — Typically called by Celery scheduler, not by users.
    Can also be called manually for testing.
    
    Endpoint: GET /api/v1/alerts/scan
    
    Response:
    {
        "success": true,
        "data": {
            "total_cases_scanned": 150,
            "newly_eligible_found": 5,
            "newly_flagged": 5,
            "skipped_already_flagged": 45,
            "errors": [],
            "scan_timestamp": "2026-08-14T10:45:00Z",
            "scan_duration_seconds": 2.34
        },
        "error": null
    }
    
    Time Complexity: O(n) where n = number of undertrial cases
    Space Complexity: O(n) for storing scan results
    
    Returns:
        StandardResponse with scan results
    
    Raises:
        HTTPException 500: If scan fails
    """
    try:
        start_time = time.time()
        
        # TODO: Replace with actual scanner logic from scheduler.py
        # scanner = CaseMonitoringScanner()
        # results = scanner.run_scan()
        
        # For now, return mock response
        mock_results = {
            "total_cases_scanned": 150,
            "newly_eligible_found": 5,
            "newly_flagged": 5,
            "skipped_already_flagged": 45,
            "errors": [],
            "scan_timestamp": datetime.now(timezone.utc),
            "scan_duration_seconds": time.time() - start_time
        }
        
        return StandardResponse(
            success=True,
            data=mock_results,
            error=None
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return StandardResponse(
        success=False,
        data=None,
        error=exc.detail
    )


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
def root():
    """Root endpoint."""
    return StandardResponse(
        success=True,
        data={
            "service": config.APP_NAME,
            "version": config.APP_VERSION,
            "endpoints": {
                "health": "/health",
                "save_config": "POST /api/v1/alerts/config",
                "list_pending": "GET /api/v1/alerts/pending",
                "trigger_scan": "GET /api/v1/alerts/scan"
            }
        },
        error=None
    )