import logging
from typing import Dict, Any
from models import CodeReviewState

logger = logging.getLogger(__name__)

def consolidation_agent(state: CodeReviewState) -> Dict[str, Any]:
    """모든 분석 결과를 통합하는 에이전트"""
    logger.info("Starting consolidation of analysis results")
    
    try:
        # 전체 결과 요약
        summary = summarize_findings(state)
        
        # 우선순위 결정
        priorities = determine_priorities(state)
        
        # 전체 점수 계산
        overall_score = calculate_overall_score(state)
        
        # 개선 권장사항
        recommendations = generate_recommendations(state)
        
        # 통합 결과
        consolidated_results = {
            "summary": summary,
            "overall_score": overall_score,
            "priorities": priorities,
            "recommendations": recommendations,
            "completion_status": state.completion_status,
            "confidence_scores": state.confidence_scores,
            "detailed_findings": {
                "security": state.security_findings.dict() if state.security_findings else None,
                "performance": state.performance_metrics.dict() if state.performance_metrics else None,
                "bugs": state.bug_analysis.dict() if state.bug_analysis else None,
                "tests": state.test_suggestions.dict() if state.test_suggestions else None
            }
        }
        
        # 상태 업데이트
        state.current_phase = "completed"
        state.completion_status["consolidation"] = True
        state.messages.append("Code review consolidation completed successfully")
        
        logger.info("Consolidation completed successfully")
        
        return consolidated_results
        
    except Exception as e:
        error_msg = f"Consolidation failed: {str(e)}"
        logger.error(error_msg)
        state.error_log.append(error_msg)
        state.completion_status["consolidation"] = False
        
        return {
            "error_log": state.error_log,
            "completion_status": state.completion_status
        }

def summarize_findings(state: CodeReviewState) -> str:
    """분석 결과 요약"""
    findings = []
    
    if state.security_findings:
        vuln_count = len(state.security_findings.vulnerabilities)
        if vuln_count > 0:
            findings.append(f"{vuln_count} security vulnerabilities detected")
    
    if state.performance_metrics:
        issue_count = len(state.performance_metrics.issues)
        if issue_count > 0:
            findings.append(f"{issue_count} performance issues identified")
    
    if state.bug_analysis:
        bug_count = len(state.bug_analysis.bugs)
        if bug_count > 0:
            findings.append(f"{bug_count} potential bugs found")
    
    if state.test_suggestions:
        test_count = len(state.test_suggestions.test_cases)
        findings.append(f"{test_count} test cases suggested")
    
    if not findings:
        return "Code review completed with no major issues found."
    
    return "Code review completed: " + ", ".join(findings) + "."

def determine_priorities(state: CodeReviewState) -> list:
    """우선순위 결정"""
    priorities = []
    
    # 보안 이슈가 최우선
    if state.security_findings and state.security_findings.vulnerabilities:
        critical_vulns = [v for v in state.security_findings.vulnerabilities if v.severity == "CRITICAL"]
        high_vulns = [v for v in state.security_findings.vulnerabilities if v.severity == "HIGH"]
        
        if critical_vulns:
            priorities.append(f"URGENT: Fix {len(critical_vulns)} critical security vulnerabilities")
        if high_vulns:
            priorities.append(f"HIGH: Address {len(high_vulns)} high-severity security issues")
    
    # 중요한 버그들
    if state.bug_analysis and state.bug_analysis.bugs:
        high_bugs = [b for b in state.bug_analysis.bugs if b.severity == "HIGH"]
        if high_bugs:
            priorities.append(f"HIGH: Fix {len(high_bugs)} critical bugs")
    
    # 성능 문제
    if state.performance_metrics and state.performance_metrics.issues:
        perf_issues = [i for i in state.performance_metrics.issues if i.severity in ["HIGH", "MEDIUM"]]
        if perf_issues:
            priorities.append(f"MEDIUM: Optimize {len(perf_issues)} performance bottlenecks")
    
    # 테스트 커버리지
    if state.test_suggestions:
        priorities.append("MEDIUM: Implement suggested test cases to improve coverage")
    
    return priorities[:5]  # 상위 5개만

def calculate_overall_score(state: CodeReviewState) -> float:
    """전체 점수 계산"""
    scores = {}
    weights = {
        "security": 0.35,
        "bugs": 0.25,
        "performance": 0.20,
        "maintainability": 0.20
    }
    
    # 보안 점수
    if state.security_findings:
        scores["security"] = state.security_findings.security_score
    else:
        scores["security"] = 8.0  # 기본값
    
    # 버그 점수 (유지보수성 점수 사용)
    if state.bug_analysis:
        scores["bugs"] = state.bug_analysis.maintainability_score
    else:
        scores["bugs"] = 8.0
    
    # 성능 점수 (복잡도 역수)
    if state.performance_metrics:
        scores["performance"] = max(0, 10 - state.performance_metrics.complexity_score)
    else:
        scores["performance"] = 7.0
    
    # 유지보수성 점수
    if state.bug_analysis:
        scores["maintainability"] = state.bug_analysis.maintainability_score
    else:
        scores["maintainability"] = 8.0
    
    # 가중 평균 계산
    overall = sum(scores[category] * weights[category] for category in scores)
    return round(overall, 1)

def generate_recommendations(state: CodeReviewState) -> list:
    """개선 권장사항 생성"""
    recommendations = []
    
    # 보안 권장사항
    if state.security_findings and state.security_findings.vulnerabilities:
        recommendations.append("Implement input validation and sanitization")
        recommendations.append("Use parameterized queries to prevent SQL injection")
        recommendations.append("Store secrets in environment variables")
    
    # 성능 권장사항
    if state.performance_metrics and state.performance_metrics.optimizations:
        recommendations.extend(state.performance_metrics.optimizations[:2])
    
    # 코드 품질 권장사항
    if state.bug_analysis:
        if state.bug_analysis.maintainability_score < 7.0:
            recommendations.append("Refactor large functions into smaller, focused units")
            recommendations.append("Add comprehensive documentation")
    
    # 테스트 권장사항
    if state.test_suggestions:
        recommendations.append("Implement unit tests for critical functions")
        recommendations.append("Add integration tests for component interactions")
    
    return recommendations[:6]  # 상위 6개 권장사항