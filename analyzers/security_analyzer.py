import ast
from typing import List
from models import SecurityVulnerability

class SecurityASTAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.vulnerabilities: List[SecurityVulnerability] = []
        self.context_stack = []
        self.imports = set()

    def visit_Call(self, node):
        func_name = self._get_func_name(node)
        
        # SQL Injection Detection
        if func_name in ['execute', 'query'] and self._has_string_formatting(node):
            self.vulnerabilities.append(SecurityVulnerability(
                type="SQL Injection",
                severity="HIGH",
                line_number=node.lineno,
                description=f"Potential SQL injection vulnerability in {func_name} call",
                cwe_id="CWE-89",
                recommendation="Use parameterized queries or prepared statements",
                confidence=0.8
            ))
        
        # Command Injection Detection
        if func_name in ['system', 'popen', 'subprocess.call', 'os.system'] and self._has_user_input(node):
            self.vulnerabilities.append(SecurityVulnerability(
                type="Command Injection",
                severity="CRITICAL",
                line_number=node.lineno,
                description=f"Potential command injection in {func_name}",
                cwe_id="CWE-78",
                recommendation="Validate and sanitize all user inputs, use subprocess with shell=False",
                confidence=0.9
            ))
        
        # Path Traversal Detection
        if func_name in ['open', 'file'] and len(node.args) > 0:
            if isinstance(node.args[0], ast.BinOp) and isinstance(node.args[0].op, ast.Add):
                self.vulnerabilities.append(SecurityVulnerability(
                    type="Path Traversal",
                    severity="MEDIUM",
                    line_number=node.lineno,
                    description="Potential path traversal vulnerability",
                    cwe_id="CWE-22",
                    recommendation="Validate file paths and use os.path.join()",
                    confidence=0.6
                ))
        
        # Weak Cryptography Detection
        if func_name in ['md5', 'sha1'] or (hasattr(node.func, 'attr') and node.func.attr in ['md5', 'sha1']):
            self.vulnerabilities.append(SecurityVulnerability(
                type="Weak Cryptography",
                severity="MEDIUM",
                line_number=node.lineno,
                description=f"Use of weak hashing algorithm: {func_name}",
                cwe_id="CWE-327",
                recommendation="Use SHA-256 or stronger hashing algorithms",
                confidence=0.95
            ))
        
        # Hardcoded Secret Detection
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                if any(keyword in arg.value.lower() for keyword in ['password', 'token', 'secret', 'key']):
                    if len(arg.value) > 8:  # Likely a secret
                        self.vulnerabilities.append(SecurityVulnerability(
                            type="Hardcoded Secret",
                            severity="HIGH",
                            line_number=node.lineno,
                            description="Potential hardcoded secret found",
                            cwe_id="CWE-798",
                            recommendation="Use environment variables or secure configuration management",
                            confidence=0.7
                        ))
        
        self.generic_visit(node)

    def _get_func_name(self, node):
        """Extract function name from call node"""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            else:
                return node.func.attr
        return "unknown"

    def _has_string_formatting(self, node):
        """Check if node contains string formatting operations"""
        for arg in node.args:
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                return True
            if isinstance(arg, ast.JoinedStr):  # f-strings
                return True
            if isinstance(arg, ast.Call) and hasattr(arg.func, 'attr') and arg.func.attr == 'format':
                return True
        return False

    def _has_user_input(self, node):
        """Check if node contains potential user input"""
        for arg in node.args:
            if isinstance(arg, ast.Name) and arg.id in ['input', 'request', 'params']:
                return True
            if isinstance(arg, ast.Attribute) and arg.attr in ['args', 'form', 'json']:
                return True
        return False