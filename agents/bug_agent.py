import ast
import logging
from typing import Dict, Any, List
from models import CodeReviewState, BugAnalysis, BugReport
from analyzers.bug_detector import BugDetector

logger = logging.getLogger(__name__)

def bug_detection_agent(state: CodeReviewState) -> Dict[str, Any]:
    """버그 감지를 수행하는 에이전트"""
    logger.info("Starting bug detection analysis")
    
    try:
        # AST 파싱을 통한 버그 패턴 분석
        tree = ast.parse(state.code_content)
        detector = BugDetector()
        detector.visit(tree)
        
        # 코드 스멜 분석
        code_smells: List[str] = []
        
        # 함수 길이 분석
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_length > 30:
                    code_smells.append(f"Long function: {node.name} ({func_length} lines)")
        
        # 클래스 분석
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 15:
                    code_smells.append(f"Large class: {node.name} ({len(methods)} methods)")
        
        # 중복 코드 패턴 (간단한 휴리스틱)
        lines = state.code_content.split('\n')
        stripped_lines = [line.strip() for line in lines if line.strip()]
        unique_lines = set(stripped_lines)
        if len(stripped_lines) > 0 and len(unique_lines) / len(stripped_lines) < 0.8:
            code_smells.append("High code duplication detected")
        
        # 기술 부채 항목
        technical_debt_items: List[str] = []
        
        # TODO/FIXME 주석 찾기
        for i, line in enumerate(lines, 1):
            if any(keyword in line.upper() for keyword in ['TODO', 'FIXME', 'HACK', 'XXX']):
                technical_debt_items.append(f"Line {i}: {line.strip()}")
        
        # 매직 넘버 감지
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in [0, 1, -1] and abs(node.value) > 1:
                    technical_debt_items.append(f"Magic number {node.value} at line {node.lineno}")
        
        # 유지보수성 점수 계산
        maintainability_score = 8.0
        
        # 버그 수에 따른 감점
        critical_bugs = [b for b in detector.bugs if b.severity == "HIGH"]
        medium_bugs = [b for b in detector.bugs if b.severity == "MEDIUM"]
        
        maintainability_score -= len(critical_bugs) * 2.0
        maintainability_score -= len(medium_bugs) * 1.0
        maintainability_score -= len(code_smells) * 0.5
        maintainability_score -= len(technical_debt_items) * 0.2
        
        maintainability_score = max(0.0, min(10.0, maintainability_score))
        
        # BugAnalysis 객체 생성
        bug_analysis = BugAnalysis(
            bugs=detector.bugs,
            code_smells=code_smells,
            maintainability_score=maintainability_score,
            technical_debt_items=technical_debt_items
        )
        
        # 상태 업데이트
        state.bug_analysis = bug_analysis
        state.completion_status["bug_detection"] = True
        
        # 신뢰도 점수
        confidence = 0.85
        if len(detector.bugs) == 0 and len(code_smells) == 0:
            confidence = 0.75  # 아무것도 발견되지 않으면 약간 낮은 신뢰도
        
        state.confidence_scores["bug_detection"] = confidence
        state.messages.append(f"Bug detection completed: found {len(detector.bugs)} bugs and {len(code_smells)} code smells")
        
        logger.info(f"Bug detection completed with {len(detector.bugs)} bugs found")
        
        return {
            "bug_analysis": bug_analysis,
            "completion_status": state.completion_status,
            "confidence_scores": state.confidence_scores,
            "messages": state.messages
        }
        
    except Exception as e:
        error_msg = f"Bug detection failed: {str(e)}"
        logger.error(error_msg)
        state.error_log.append(error_msg)
        state.completion_status["bug_detection"] = False
        
        return {
            "error_log": state.error_log,
            "completion_status": state.completion_status
        }