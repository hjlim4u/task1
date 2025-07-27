# Multi-Agent Code Review System - Main Application
# File: main.py

import logging
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our modules
from config import settings
from models import (
    CodeReviewState, ReviewRequest, ReviewResponse, ReviewResult
)
from storage import storage
from workflow import build_code_review_workflow

# Logging setup
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# FastAPI Application
app = FastAPI(
    title="Multi-Agent Code Review System",
    version="1.0.0",
    description="Automated code review using specialized AI agents"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/api/v1/review", response_model=ReviewResponse)
async def create_code_review(
        request: ReviewRequest,
        background_tasks: BackgroundTasks
):
    """Create a new code review"""
    review_id = str(uuid4())
    storage.create_review(review_id)
    
    background_tasks.add_task(
        process_code_review,
        review_id,
        request.code,
        request.filename,
        request.language
    )

    return ReviewResponse(
        review_id=review_id,
        status="processing",
        message="Code review started"
    )

@app.get("/api/v1/review/{review_id}", response_model=ReviewResult)
async def get_review_status(review_id: str):
    """Get code review results"""
    review = storage.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return ReviewResult(
        review_id=review.id,
        status=review.status,
        results=review.results or {},
        created_at=review.created_at,
        completed_at=review.completed_at
    )

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Background Processing
async def process_code_review(review_id: str, code: str, filename: str, language: str):
    """Process code review in background"""
    logger.info(f"Processing review {review_id}")

    try:
        workflow = build_code_review_workflow()
        
        initial_state = CodeReviewState(
            code_content=code,
            file_path=filename,
            language=language,
            current_phase="starting",
            completion_status={
                "security": False,
                "performance": False,
                "bug_detection": False,
                "test_generation": False,
                "consolidation": False
            },
            error_log=[],
            confidence_scores={},
            messages=[]
        )

        config = {"configurable": {"thread_id": review_id}}
        final_state = await workflow.ainvoke(initial_state, config)

        # Update storage with results
        results = {
            "security": final_state.get("security_findings").dict() if final_state.get("security_findings") else None,
            "performance": final_state.get("performance_metrics").dict() if final_state.get("performance_metrics") else None,
            "bugs": final_state.get("bug_analysis").dict() if final_state.get("bug_analysis") else None,
            "tests": final_state.get("test_suggestions").dict() if final_state.get("test_suggestions") else None,
            "summary": final_state.get("completion_status")
        }

        storage.update_review(
            review_id,
            status="completed",
            completed_at=datetime.utcnow(),
            results=results
        )

        logger.info(f"Review {review_id} completed successfully")

    except Exception as e:
        logger.error(f"Review {review_id} failed: {e}")
        storage.update_review(
            review_id,
            status="failed",
            results={"error": str(e)}
        )

# Main Entry Point
if __name__ == "__main__":
    logger.info("Starting Multi-Agent Code Review System")
    uvicorn.run(
        app, 
        host=settings.app_host, 
        port=settings.app_port
    )