import ast
import logging
from typing import Dict, Any
from models import CodeReviewState, SecurityAnalysis, SecurityVulnerability
from analyzers.security_analyzer import SecurityASTAnalyzer

logger = logging.getLogger(__name__)

def security_analysis_agent(state: CodeReviewState) -> Dict[str, Any]:
    """보안 분석을 수행하는 에이전트"""
    logger.info("Starting security analysis")
    
    try:
        # AST 파싱을 통한 정적 분석
        tree = ast.parse(state.code_content)
        analyzer = SecurityASTAnalyzer()
        analyzer.visit(tree)
        
        # 심각도별 분류
        critical_vulns = [v for v in analyzer.vulnerabilities if v.severity == "CRITICAL"]
        high_vulns = [v for v in analyzer.vulnerabilities if v.severity == "HIGH"]
        medium_vulns = [v for v in analyzer.vulnerabilities if v.severity == "MEDIUM"]
        low_vulns = [v for v in analyzer.vulnerabilities if v.severity == "LOW"]
        
        # 전체적인 위험도 평가
        total_vulns = len(analyzer.vulnerabilities)
        if len(critical_vulns) > 0:
            overall_risk = "CRITICAL"
            security_score = 2.0
        elif len(high_vulns) > 2:
            overall_risk = "HIGH"
            security_score = 3.5
        elif len(high_vulns) > 0 or len(medium_vulns) > 3:
            overall_risk = "MEDIUM"
            security_score = 6.0
        elif total_vulns > 0:
            overall_risk = "LOW"
            security_score = 8.0
        else:
            overall_risk = "MINIMAL"
            security_score = 9.5
        
        # 분석 결과 요약
        summary_parts = []
        if critical_vulns:
            summary_parts.append(f"{len(critical_vulns)} critical vulnerabilities")
        if high_vulns:
            summary_parts.append(f"{len(high_vulns)} high-risk issues")
        if medium_vulns:
            summary_parts.append(f"{len(medium_vulns)} medium-risk issues")
        if low_vulns:
            summary_parts.append(f"{len(low_vulns)} low-risk issues")
        
        summary = f"Found {total_vulns} total security issues: " + ", ".join(summary_parts) if summary_parts else "No security vulnerabilities detected"
        
        # SecurityAnalysis 객체 생성
        security_analysis = SecurityAnalysis(
            vulnerabilities=analyzer.vulnerabilities,
            overall_risk=overall_risk,
            security_score=security_score,
            summary=summary
        )
        
        # 상태 업데이트
        state.security_findings = security_analysis
        state.completion_status["security"] = True
        state.confidence_scores["security"] = min(0.9, 0.6 + (security_score / 10) * 0.3)
        state.messages.append(f"Security analysis completed: {summary}")
        
        logger.info(f"Security analysis completed with {total_vulns} vulnerabilities found")
        
        return {
            "security_findings": security_analysis,
            "completion_status": state.completion_status,
            "confidence_scores": state.confidence_scores,
            "messages": state.messages
        }
        
    except Exception as e:
        error_msg = f"Security analysis failed: {str(e)}"
        logger.error(error_msg)
        state.error_log.append(error_msg)
        state.completion_status["security"] = False
        
        return {
            "error_log": state.error_log,
            "completion_status": state.completion_status
        }