import ast
from typing import List
from models import PerformanceIssue

class PerformancePatternAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.issues: List[PerformanceIssue] = []
        self.loop_depth = 0

    def visit_For(self, node):
        self.loop_depth += 1
        
        # Nested loop detection
        if self.loop_depth > 2:
            self.issues.append(PerformanceIssue(
                type="Nested Loops",
                severity="MEDIUM",
                line_number=node.lineno,
                description=f"Deeply nested loops detected (depth: {self.loop_depth})",
                impact="O(n^{}) time complexity".format(self.loop_depth),
                optimization="Consider algorithm optimization or caching",
                estimated_improvement="10-90% performance improvement possible"
            ))
        
        # List comprehension vs loop
        if isinstance(node.iter, ast.Call) and self._get_func_name(node.iter) == 'range':
            for stmt in node.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    if hasattr(stmt.value.func, 'attr') and stmt.value.func.attr == 'append':
                        self.issues.append(PerformanceIssue(
                            type="Inefficient Loop",
                            severity="LOW",
                            line_number=node.lineno,
                            description="Loop with append could be optimized with list comprehension",
                            impact="Moderate performance impact",
                            optimization="Use list comprehension instead of loop with append",
                            estimated_improvement="20-50% performance improvement"
                        ))
        
        # String concatenation in loop
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                if isinstance(stmt.value, ast.BinOp) and isinstance(stmt.value.op, ast.Add):
                    if any(isinstance(operand, ast.Constant) and isinstance(operand.value, str) 
                           for operand in [stmt.value.left, stmt.value.right]):
                        self.issues.append(PerformanceIssue(
                            type="String Concatenation in Loop",
                            severity="MEDIUM",
                            line_number=stmt.lineno,
                            description="String concatenation in loop is inefficient",
                            impact="O(n²) complexity for string operations",
                            optimization="Use list.join() or f-strings",
                            estimated_improvement="50-80% performance improvement for large datasets"
                        ))
        
        self.generic_visit(node)
        self.loop_depth -= 1

    def _get_func_name(self, node):
        """Extract function name from call node"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return "unknown"