from typing import Dict, Any
from langgraph.graph import StateGraph, END
from models import CodeReviewState
from agents import (
    security_analysis_agent,
    performance_analysis_agent,
    bug_detection_agent,
    test_generation_agent,
    consolidation_agent
)

def should_continue(state: CodeReviewState) -> str:
    """워크플로우 계속 여부 결정"""
    # 모든 단계가 완료되었는지 확인
    required_phases = ["security", "performance", "bug_detection", "test_generation"]
    completed_phases = [phase for phase in required_phases if state.completion_status.get(phase, False)]
    
    if len(completed_phases) < len(required_phases):
        # 다음 미완료 단계로 이동
        next_phase = next(phase for phase in required_phases if not state.completion_status.get(phase, False))
        state.current_phase = next_phase
        return next_phase
    else:
        # 모든 단계 완료, 통합 단계로
        state.current_phase = "consolidation"
        return "consolidation"

def build_code_review_workflow() -> StateGraph:
    """코드 리뷰 워크플로우 구성"""
    workflow = StateGraph(CodeReviewState)
    
    # 노드 추가
    workflow.add_node("security", security_analysis_agent)
    workflow.add_node("performance", performance_analysis_agent)
    workflow.add_node("bug_detection", bug_detection_agent)
    workflow.add_node("test_generation", test_generation_agent)
    workflow.add_node("consolidation", consolidation_agent)
    
    # 시작점 설정
    workflow.set_entry_point("security")
    
    # 엣지 추가 (조건부 라우팅)
    workflow.add_conditional_edges(
        "security",
        should_continue,
        {
            "performance": "performance",
            "bug_detection": "bug_detection",
            "test_generation": "test_generation",
            "consolidation": "consolidation"
        }
    )
    
    workflow.add_conditional_edges(
        "performance",
        should_continue,
        {
            "security": "security",
            "bug_detection": "bug_detection",
            "test_generation": "test_generation",
            "consolidation": "consolidation"
        }
    )
    
    workflow.add_conditional_edges(
        "bug_detection",
        should_continue,
        {
            "security": "security",
            "performance": "performance",
            "test_generation": "test_generation",
            "consolidation": "consolidation"
        }
    )
    
    workflow.add_conditional_edges(
        "test_generation",
        should_continue,
        {
            "security": "security",
            "performance": "performance",
            "bug_detection": "bug_detection",
            "consolidation": "consolidation"
        }
    )
    
    # 통합 단계는 종료로
    workflow.add_edge("consolidation", END)
    
    return workflow.compile()