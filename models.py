from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

# Pydantic Models
class SecurityVulnerability(BaseModel):
    type: str
    severity: str
    line_number: int
    description: str
    cwe_id: Optional[str] = None
    recommendation: str
    confidence: float

class SecurityAnalysis(BaseModel):
    vulnerabilities: List[SecurityVulnerability]
    overall_risk: str
    security_score: float
    summary: str

class PerformanceIssue(BaseModel):
    type: str
    severity: str
    line_number: int
    description: str
    impact: str
    optimization: str
    estimated_improvement: str

class PerformanceAnalysis(BaseModel):
    issues: List[PerformanceIssue]
    complexity_score: float
    memory_efficiency: float
    optimizations: List[str]
    benchmark_suggestions: List[str]

class BugReport(BaseModel):
    type: str
    severity: str
    line_number: int
    description: str
    fix_suggestion: str
    confidence: float

class BugAnalysis(BaseModel):
    bugs: List[BugReport]
    code_smells: List[str]
    maintainability_score: float
    technical_debt_items: List[str]

class TestSuggestion(BaseModel):
    test_type: str
    function_name: str
    test_code: str
    description: str
    coverage_improvement: float
    dependencies: List[str]

class TestGenerationResult(BaseModel):
    test_cases: List[TestSuggestion]
    mock_requirements: List[str]
    setup_instructions: str
    coverage_estimate: float
    framework_recommendations: List[str]

class CodeReviewState(BaseModel):
    code_content: str
    file_path: str
    language: str
    security_findings: Optional[SecurityAnalysis] = None
    performance_metrics: Optional[PerformanceAnalysis] = None
    bug_analysis: Optional[BugAnalysis] = None
    test_suggestions: Optional[TestGenerationResult] = None
    current_phase: str
    completion_status: Dict[str, bool]
    error_log: List[str]
    confidence_scores: Dict[str, float]
    messages: List[str]

# API Models
class ReviewRequest(BaseModel):
    code: str
    filename: str
    language: Optional[str] = "python"

class ReviewResponse(BaseModel):
    review_id: str
    status: str
    message: str

class ReviewResult(BaseModel):
    review_id: str
    status: str
    results: dict
    created_at: datetime
    completed_at: Optional[datetime] = None

# In-memory storage model
class InMemoryCodeReview(BaseModel):
    id: str
    user_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[dict] = None
    metrics: Optional[dict] = None
    files_count: int = 1