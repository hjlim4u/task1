import ast
import logging
from typing import Dict, Any
from models import CodeReviewState, PerformanceAnalysis, PerformanceIssue
from analyzers.performance_analyzer import PerformancePatternAnalyzer

logger = logging.getLogger(__name__)

def performance_analysis_agent(state: CodeReviewState) -> Dict[str, Any]:
    """성능 분석을 수행하는 에이전트"""
    logger.info("Starting performance analysis")
    
    try:
        # AST 파싱을 통한 성능 패턴 분석
        tree = ast.parse(state.code_content)
        analyzer = PerformancePatternAnalyzer()
        analyzer.visit(tree)
        
        # 복잡도 점수 계산 (간단한 휴리스틱)
        complexity_score = 5.0  # 기본 점수
        
        # 코드 라인 수에 따른 복잡도 조정
        lines_count = len(state.code_content.split('\n'))
        if lines_count > 100:
            complexity_score += 1.0
        if lines_count > 500:
            complexity_score += 2.0
            
        # 발견된 성능 이슈에 따른 복잡도 조정
        critical_issues = [i for i in analyzer.issues if i.severity == "HIGH"]
        medium_issues = [i for i in analyzer.issues if i.severity == "MEDIUM"]
        
        complexity_score += len(critical_issues) * 2.0
        complexity_score += len(medium_issues) * 1.0
        
        # 메모리 효율성 점수 (0-10)
        memory_efficiency = 8.0
        for issue in analyzer.issues:
            if "memory" in issue.description.lower() or "string concatenation" in issue.type.lower():
                memory_efficiency -= 1.5
        memory_efficiency = max(0.0, min(10.0, memory_efficiency))
        
        # 최적화 제안
        optimizations = []
        if any("nested" in issue.type.lower() for issue in analyzer.issues):
            optimizations.append("Consider algorithm optimization for nested operations")
        if any("string" in issue.type.lower() for issue in analyzer.issues):
            optimizations.append("Use efficient string operations (join, f-strings)")
        if any("loop" in issue.type.lower() for issue in analyzer.issues):
            optimizations.append("Replace loops with list comprehensions where applicable")
        
        if not optimizations:
            optimizations.append("Code shows good performance patterns")
        
        # 벤치마크 제안
        benchmark_suggestions = [
            "Add timing decorators to critical functions",
            "Use cProfile for detailed performance profiling",
            "Consider memory profiling with memory_profiler",
            "Set up performance regression tests"
        ]
        
        # PerformanceAnalysis 객체 생성
        performance_analysis = PerformanceAnalysis(
            issues=analyzer.issues,
            complexity_score=complexity_score,
            memory_efficiency=memory_efficiency,
            optimizations=optimizations,
            benchmark_suggestions=benchmark_suggestions
        )
        
        # 상태 업데이트
        state.performance_metrics = performance_analysis
        state.completion_status["performance"] = True
        
        # 신뢰도 점수 계산
        confidence = 0.8
        if len(analyzer.issues) == 0:
            confidence = 0.7  # 이슈가 없을 때는 약간 낮은 신뢰도
        
        state.confidence_scores["performance"] = confidence
        state.messages.append(f"Performance analysis completed: found {len(analyzer.issues)} performance issues")
        
        logger.info(f"Performance analysis completed with {len(analyzer.issues)} issues found")
        
        return {
            "performance_metrics": performance_analysis,
            "completion_status": state.completion_status,
            "confidence_scores": state.confidence_scores,
            "messages": state.messages
        }
        
    except Exception as e:
        error_msg = f"Performance analysis failed: {str(e)}"
        logger.error(error_msg)
        state.error_log.append(error_msg)
        state.completion_status["performance"] = False
        
        return {
            "error_log": state.error_log,
            "completion_status": state.completion_status
        }