import ast
from typing import List
from models import BugReport

class BugDetector(ast.NodeVisitor):
    def __init__(self):
        self.bugs: List[BugReport] = []

    def visit_FunctionDef(self, node):
        # Function without docstring
        if not ast.get_docstring(node):
            self.bugs.append(BugReport(
                type="Documentation",
                severity="LOW",
                line_number=node.lineno,
                description=f"Function '{node.name}' lacks documentation",
                fix_suggestion="Add docstring to explain function purpose, parameters, and return value",
                confidence=0.9
            ))
        
        # Function with too many parameters
        if len(node.args.args) > 5:
            self.bugs.append(BugReport(
                type="Code Smell",
                severity="MEDIUM",
                line_number=node.lineno,
                description=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                fix_suggestion="Consider using a data class or dictionary to group parameters",
                confidence=0.8
            ))
        
        # Function too long
        function_length = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
        if function_length > 50:
            self.bugs.append(BugReport(
                type="Code Smell",
                severity="MEDIUM",
                line_number=node.lineno,
                description=f"Function '{node.name}' is too long ({function_length} lines)",
                fix_suggestion="Break down into smaller, more focused functions",
                confidence=0.7
            ))
        
        # Empty except blocks
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.ExceptHandler) and len(stmt.body) == 1:
                if isinstance(stmt.body[0], ast.Pass):
                    self.bugs.append(BugReport(
                        type="Error Handling",
                        severity="HIGH",
                        line_number=stmt.lineno,
                        description="Empty except block silently ignores errors",
                        fix_suggestion="Add proper error handling or at least logging",
                        confidence=0.95
                    ))
        
        self.generic_visit(node)

    def visit_Compare(self, node):
        # Using 'is' with strings/numbers
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.Is):
            if isinstance(node.left, ast.Constant) or isinstance(node.comparators[0], ast.Constant):
                left_is_small_int = (isinstance(node.left, ast.Constant) and 
                                   isinstance(node.left.value, int) and 
                                   -5 <= node.left.value <= 256)
                right_is_small_int = (isinstance(node.comparators[0], ast.Constant) and 
                                     isinstance(node.comparators[0].value, int) and 
                                     -5 <= node.comparators[0].value <= 256)
                
                if not (left_is_small_int or right_is_small_int):
                    self.bugs.append(BugReport(
                        type="Logic Error",
                        severity="MEDIUM",
                        line_number=node.lineno,
                        description="Using 'is' for value comparison instead of '=='",
                        fix_suggestion="Use '==' for value comparison, 'is' only for identity comparison",
                        confidence=0.9
                    ))
        
        # Comparison with None using ==
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
            if (isinstance(node.left, ast.Constant) and node.left.value is None) or \
               (isinstance(node.comparators[0], ast.Constant) and node.comparators[0].value is None):
                self.bugs.append(BugReport(
                    type="Style Issue",
                    severity="LOW",
                    line_number=node.lineno,
                    description="Using '==' with None instead of 'is'",
                    fix_suggestion="Use 'is None' or 'is not None' for None comparisons",
                    confidence=0.85
                ))
        
        self.generic_visit(node)