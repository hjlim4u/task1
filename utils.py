import ast
import re
from typing import List, Dict, Any

def extract_functions_from_code(code_content: str) -> List[Dict[str, Any]]:
    """코드에서 함수 정보를 추출합니다."""
    try:
        tree = ast.parse(code_content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': getattr(node, 'end_lineno', node.lineno),
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node),
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                })
        
        return functions
    except SyntaxError:
        return []

def summarize_findings(state) -> str:
    """분석 결과를 요약합니다."""
    summary_parts = []
    
    # 보안 분석 요약
    if hasattr(state, 'security_findings') and state.security_findings:
        vuln_count = len(state.security_findings.vulnerabilities)
        if vuln_count > 0:
            critical = len([v for v in state.security_findings.vulnerabilities if v.severity == "CRITICAL"])
            high = len([v for v in state.security_findings.vulnerabilities if v.severity == "HIGH"])
            
            if critical > 0:
                summary_parts.append(f"{critical} critical security issues")
            if high > 0:
                summary_parts.append(f"{high} high-risk security issues")
    
    # 성능 분석 요약
    if hasattr(state, 'performance_metrics') and state.performance_metrics:
        if state.performance_metrics.long_running_queries:
            summary_parts.append(f"{len(state.performance_metrics.long_running_queries)} long-running queries detected")
    
    # 코드 품질 분석 요약
    if hasattr(state, 'code_quality_findings') and state.code_quality_findings:
        code_smells_count = len(state.code_quality_findings.code_smells)
        if code_smells_count > 0:
            summary_parts.append(f"{code_smells_count} code smells identified")
    
    if summary_parts:
        return " and ".join(summary_parts) + " were found."
    else:
        return "No issues were found."