import ast
import logging
from typing import Dict, Any, List
from models import CodeReviewState, TestGenerationResult, TestSuggestion

logger = logging.getLogger(__name__)

def test_generation_agent(state: CodeReviewState) -> Dict[str, Any]:
    """테스트 생성을 수행하는 에이전트"""
    logger.info("Starting test generation analysis")
    
    try:
        # AST 파싱을 통한 함수 추출
        tree = ast.parse(state.code_content)
        functions = extract_functions_from_code(tree)
        
        test_cases = []
        
        for func_info in functions:
            func_name = func_info['name']
            func_args = func_info['args']
            func_line = func_info['line']
            
            # 단위 테스트 제안
            unit_test = TestSuggestion(
                test_type="Unit Test",
                function_name=func_name,
                test_code=generate_unit_test_template(func_name, func_args),
                description=f"Unit test for {func_name} function",
                coverage_improvement=15.0,
                dependencies=["pytest"]
            )
            test_cases.append(unit_test)
            
            # 엣지 케이스 테스트 제안
            if func_args:
                edge_test = TestSuggestion(
                    test_type="Edge Case Test",
                    function_name=func_name,
                    test_code=generate_edge_case_test(func_name, func_args),
                    description=f"Edge case testing for {func_name}",
                    coverage_improvement=10.0,
                    dependencies=["pytest", "hypothesis"]
                )
                test_cases.append(edge_test)
        
        # 클래스 메서드 테스트
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_test = TestSuggestion(
                    test_type="Class Test",
                    function_name=node.name,
                    test_code=generate_class_test_template(node.name),
                    description=f"Test suite for {node.name} class",
                    coverage_improvement=20.0,
                    dependencies=["pytest", "unittest.mock"]
                )
                test_cases.append(class_test)
        
        # 통합 테스트 제안
        if len(functions) > 3:
            integration_test = TestSuggestion(
                test_type="Integration Test",
                function_name="integration_tests",
                test_code=generate_integration_test_template(),
                description="Integration tests for component interactions",
                coverage_improvement=25.0,
                dependencies=["pytest", "pytest-asyncio"]
            )
            test_cases.append(integration_test)
        
        # Mock 요구사항 분석
        mock_requirements = []
        for line in state.code_content.split('\n'):
            if any(keyword in line for keyword in ['requests.', 'open(', 'database', 'redis', 'api']):
                mock_requirements.append("External dependencies detected - consider mocking")
        
        # 설정 지침
        setup_instructions = """
1. Install test dependencies: pip install pytest pytest-cov
2. Create tests/ directory structure
3. Configure pytest.ini for test discovery
4. Set up CI/CD pipeline for automated testing
5. Add coverage reporting with pytest-cov
        """.strip()
        
        # 커버리지 추정
        total_functions = len(functions)
        estimated_coverage = min(85.0, 40.0 + (len(test_cases) * 8))
        
        # 프레임워크 추천
        framework_recommendations = [
            "pytest - for general testing framework",
            "unittest.mock - for mocking dependencies",
            "hypothesis - for property-based testing",
            "pytest-asyncio - if async code is present"
        ]
        
        # TestGenerationResult 객체 생성
        test_generation = TestGenerationResult(
            test_cases=test_cases,
            mock_requirements=mock_requirements,
            setup_instructions=setup_instructions,
            coverage_estimate=estimated_coverage,
            framework_recommendations=framework_recommendations
        )
        
        # 상태 업데이트
        state.test_suggestions = test_generation
        state.completion_status["test_generation"] = True
        state.confidence_scores["test_generation"] = 0.8
        state.messages.append(f"Test generation completed: {len(test_cases)} test suggestions generated")
        
        logger.info(f"Test generation completed with {len(test_cases)} test cases suggested")
        
        return {
            "test_suggestions": test_generation,
            "completion_status": state.completion_status,
            "confidence_scores": state.confidence_scores,
            "messages": state.messages
        }
        
    except Exception as e:
        error_msg = f"Test generation failed: {str(e)}"
        logger.error(error_msg)
        state.error_log.append(error_msg)
        state.completion_status["test_generation"] = False
        
        return {
            "error_log": state.error_log,
            "completion_status": state.completion_status
        }

def extract_functions_from_code(tree):
    """코드에서 함수 정보 추출"""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'args': [arg.arg for arg in node.args.args],
                'line': node.lineno
            })
    return functions

def generate_unit_test_template(func_name: str, args: List[str]) -> str:
    """단위 테스트 템플릿 생성"""
    args_str = ", ".join([f"{arg}_value" for arg in args])
    
    return f"""
def test_{func_name}():
    # Arrange
    {args_str if args_str else "# Set up test data"}
    
    # Act
    result = {func_name}({args_str})
    
    # Assert
    assert result is not None
    # Add specific assertions based on expected behavior
    """.strip()

def generate_edge_case_test(func_name: str, args: List[str]) -> str:
    """엣지 케이스 테스트 템플릿 생성"""
    return f"""
def test_{func_name}_edge_cases():
    # Test with None values
    # Test with empty values
    # Test with boundary conditions
    # Test with invalid inputs
    
    # Example:
    with pytest.raises(ValueError):
        {func_name}(None)
    """.strip()

def generate_class_test_template(class_name: str) -> str:
    """클래스 테스트 템플릿 생성"""
    return f"""
class Test{class_name}:
    def setup_method(self):
        self.instance = {class_name}()
    
    def test_initialization(self):
        assert isinstance(self.instance, {class_name})
    
    def teardown_method(self):
        # Clean up after each test
        pass
    """.strip()

def generate_integration_test_template() -> str:
    """통합 테스트 템플릿 생성"""
    return """
def test_component_integration():
    # Test interaction between multiple components
    # Verify data flow and communication
    # Test error propagation
    pass
    """.strip()