# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Validator - Validates and fixes generated strategy code
"""

import os
import sys
import re
import subprocess
import tempfile



class CodeValidator:
    """Validates and fixes generated Python code"""
    
    def __init__(self, python_executable = "python3"):
        """Initialize validator"""
        self.python_executable = python_executable
        
    def validate_file(self, filepath):
        """
        Validate a Python file and return issues
        
        Returns:
            Dictionary with validation results
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return {"valid": False, "errors": ["File not found"], "warnings": []}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common issues
        issues = self._check_static_issues(content)
        
        # Try to run syntax check
        syntax_errors = self._check_syntax(filepath)
        if syntax_errors:
            issues["errors"].extend(syntax_errors)
        
        # Check for runtime import errors
        import_errors = self._check_imports(filepath)
        if import_errors:
            issues["errors"].extend(import_errors)
        
        valid = len(issues["errors"]) == 0
        return {
            "valid": valid,
            "errors": issues["errors"],
            "warnings": issues["warnings"],
            "filepath"(filepath)
        }
    
    def _check_static_issues(self, content):
        """Check for static code issues"""
        errors = []
        warnings = []
        
        # Check for Python version compatibility (now supports 3.6+)
        # Note: f-strings are now allowed for Python 3.6+
        
        # Check for type annotations without imports
        type_annotations = re.findall(r'->\s*(\w+\[.*?\]|\w+)', content)
        for annotation in type_annotations:
            if annotation.startswith('List') or annotation.startswith('Dict') or annotation.startswith('Optional'):
                if 'from typing import' not in content and 'import typing' not in content:
                    errors.append("Type annotation '{}' found but typing module not imported".format(annotation))
        
        # Check for missing encoding declaration
        lines = content.split('\n')
        has_encoding = False
        for line in lines[:2]:
            if 'coding: utf-8' in line or 'coding=utf-8' in line:
                has_encoding = True
                break
        
        if not has_encoding and any(ord(char) > 127 for char in content[:1000]):
            warnings.append("Non-ASCII characters found but no encoding declaration")
        
        # Check for common API wrapper issues
        if 'hyperliquid_api' in content and 'from hyperliquid_api import' in content:
            # Check if api_wrappers path is added
            if 'sys.path.insert' not in content and 'sys.path.append' not in content:
                warnings.append("API wrapper import found but sys.path not modified")
        
        return {"errors": errors, "warnings": warnings}
    
    def _check_syntax(self, filepath: Path):
        """Check Python syntax"""
        try:
            # Use python -m py_compile for syntax checking
            result = subprocess.run(
                [self.python_executable, "-m", "py_compile", str(filepath)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # Parse error output
                errors = []
                for line in result.stderr.split('\n'):
                    if 'SyntaxError' in line or 'Error' in line:
                        errors.append(line.strip())
                return errors if errors else ["Unknown syntax error"]
            
        except subprocess.TimeoutExpired:
            return ["Syntax check timed out"]
        except Exception as e:
            return ["Syntax check failed: {}".format(str(e))]
        
        return []
    
    def _check_imports(self, filepath: Path):
        """Check for import errors"""
        try:
            # Create a temporary test script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                test_script = """
import sys
import os

# Try to add common paths
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'api_wrappers'))

try:
    import {module_name}
    print("SUCCESS: Import successful")
except ImportError as e:
    print("IMPORT_ERROR: " + str(e))
except SyntaxError as e:
    print("SYNTAX_ERROR: " + str(e))
except Exception as e:
    print("OTHER_ERROR: " + str(e))
""".format(module_name=filepath.stem)
                f.write(test_script)
                temp_file = f.name
            
            # Run the test script
            result = subprocess.run(
                [self.python_executable, temp_file],
                capture_output=True,
                text=True,
                cwd=filepath.parent,
                timeout=10
            )
            
            # Clean up
            os.unlink(temp_file)
            
            # Parse results
            errors = []
            for line in result.stdout.split('\n') + result.stderr.split('\n'):
                if line.startswith('IMPORT_ERROR:'):
                    errors.append(line.replace('IMPORT_ERROR:', '').strip())
                elif line.startswith('SYNTAX_ERROR:'):
                    errors.append(line.replace('SYNTAX_ERROR:', '').strip())
                elif line.startswith('OTHER_ERROR:'):
                    errors.append(line.replace('OTHER_ERROR:', '').strip())
            
            return errors
            
        except Exception as e:
            return ["Import check failed: {}".format(str(e))]
    
    def fix_common_issues(self, filepath):
        """
        Fix common issues in Python file
        
        Returns:
            Dictionary with fix results
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return {"fixed": False, "changes": [], "errors": ["File not found"]}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Fix 1: Add encoding declaration if missing
        if '# -*- coding: utf-8 -*-' not in content:
            lines = content.split('\n')
            if lines[0].startswith('#!'):
                lines.insert(1, '# -*- coding: utf-8 -*-')
                changes.append("Added encoding declaration")
            else:
                lines.insert(0, '# -*- coding: utf-8 -*-')
                changes.append("Added encoding declaration")
            content = '\n'.join(lines)
        
        # Fix 2: Remove type annotations if typing not imported
        if '
            # Remove -> Type annotations
            content = re.sub(r'\)\s*->\s*\w+\[.*?\]\s*:', '):', content)
            content = re.sub(r'\)\s*->\s*\w+\s*:', '):', content)
            
            # Remove : Type annotations in function parameters
            content = re.sub(r':\s*\w+\[.*?\]', '', content)
            content = re.sub(r':\s*\w+', '', content)
            
            changes.append("Removed type annotations (typing module not imported)")
        
        # Fix 3: Add sys.path modification for api_wrappers
        if 'from hyperliquid_api import' in content and 'sys.path.insert' not in content:
            # Find imports section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'import' in line and ('hyperliquid_api' in line or 'HyperliquidClient' in line):
                    # Add sys.path before imports
                    path_line = 'sys.path.insert(0, str(Path(__file__).parent.parent / "api_wrappers"))'
                    if i > 0:
                        lines.insert(i, path_line)
                        lines.insert(i, '')
                        lines.insert(i, 'import sys')
                        changes.append("Added sys.path modification for api_wrappers")
                    break
            content = '\n'.join(lines)
        
        # Fix 4: Check Python version compatibility
        # Note: f-strings are now allowed for Python 3.6+
        # We'll check for Python 3.5 incompatible features
        if '"' in content or "'" in content:
            # f-strings are now allowed for Python 3.6+
            # Just log that we found them
            changes.append("Found f-strings (Python 3.6+ compatible)")
        
        # Write back if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "fixed": True,
                "changes": changes,
                "filepath"(filepath)
            }
        else:
            return {
                "fixed": False,
                "changes": ["No changes needed"],
                "filepath"(filepath)
            }
    
    def validate_and_fix(self, filepath, max_iterations = 3):
        """
        Validate and fix code until it's valid or max iterations reached
        
        Returns:
            Dictionary with final validation results
        """
        filepath = Path(filepath)
        all_changes = []
        
        for iteration in range(max_iterations):
            # Validate
            validation = self.validate_file(str(filepath))
            
            if validation["valid"]:
                return {
                    "valid": True,
                    "iterations": iteration + 1,
                    "changes": all_changes,
                    "errors": [],
                    "warnings": validation["warnings"],
                    "filepath"(filepath)
                }
            
            # Try to fix
            fix_result = self.fix_common_issues(str(filepath))
            
            if not fix_result["fixed"]:
                # Couldn't fix the issues
                return {
                    "valid": False,
                    "iterations": iteration + 1,
                    "changes": all_changes,
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                    "filepath"(filepath)
                }
            
            all_changes.extend(fix_result["changes"])
        
        # Max iterations reached
        final_validation = self.validate_file(str(filepath))
        return {
            "valid": final_validation["valid"],
            "iterations": max_iterations,
            "changes": all_changes,
            "errors": final_validation["errors"],
            "warnings": final_validation["warnings"],
            "filepath"(filepath)
        }

def validate_strategy_directory(directory):
    """
    Validate all Python files in a strategy directory
    
    Returns:
        Dictionary with validation results for all files
    """
    directory = Path(directory)
    if not directory.exists():
        return {"valid": False, "errors": ["Directory not found"], "files": {}}
    
    validator = CodeValidator()
    results = {}
    all_valid = True
    
    # Find all Python files
    python_files = list(directory.glob("*.py"))
    
    for py_file in python_files:
        print("Validating: {}".format(py_file.name))
        result = validator.validate_and_fix(str(py_file))
        results[py_file.name] = result
        
        if not result["valid"]:
            all_valid = False
            print("  ❌ Validation failed")
            for error in result["errors"]:
                print("    - {}".format(error))
        else:
            print("  ✅ Validation passed")
            if result["changes"]:
                print("    Changes made: {}".format(", ".join(result["changes"])))
    
    return {
        "valid": all_valid,
        "files": results,
        "directory"(directory)
    }

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate and fix generated strategy code")
    parser.add_argument("path", help="Path to Python file or directory")
    parser.add_argument("--fix", action="store_true", help="Automatically fix issues")
    parser.add_argument("--python", default="python3", help="Python executable to use")
    
    args = parser.parse_args()
    
    validator = CodeValidator(args.python)
    path = Path(args.path)
    
    if path.is_file() and path.suffix == '.py':
        if args.fix:
            result = validator.validate_and_fix(str(path))
        else:
            result = validator.validate_file(str(path))
        
        print("\nValidation results for: {}".format(path.name))
        print("=" * 60)
        
        if result["valid"]:
            print("✅ Code is valid!")
        else:
            print("❌ Code has issues:")
            for error in result.get("errors", []):
                print("  - {}".format(error))
        
        if result.get("warnings"):
            print("\n⚠️  Warnings:")
            for warning in result["warnings"]:
                print("  - {}".format(warning))
        
        if result.get("changes"):
            print("\n🔧 Changes made:")
            for change in result["changes"]:
                print("  - {}".format(change))
        
        if result.get("iterations"):
            print("\n🔄 Fix iterations: {}".format(result["iterations"]))
    
    elif path.is_dir():
        result = validate_strategy_directory(str(path))
        
        print("\nValidation results for directory: {}".format(path.name))
        print("=" * 60)
        
        if result["valid"]:
            print("✅ All files are valid!")
        else:
            print("❌ Some files have issues")
        
        for filename, file_result in result["files"].items():
            print("\n📄 {}: {}".format(
                filename,
                "✅ Valid" if file_result["valid"] else "❌ Invalid"
            ))
            
            if not file_result["valid"] and file_result.get("errors"):
                for error in file_result["errors"]:
                    print("    - {}".format(error))
            
            if file_result.get("changes"):
                print("    Changes: {}".format(", ".join(file_result["changes"])))
    
    else:
        print("Error: Path must be a Python file or directory")
        return 1
    
    return 0 if result.get("valid", False) else 1

if __name__ == "__main__":
    sys.exit(main())