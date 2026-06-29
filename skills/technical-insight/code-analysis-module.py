#!/usr/bin/env python3
"""
Code Analysis Module for Technical Insight Skill
Analyzes GitHub repositories and extracts architectural information
"""

import os
import json
import subprocess
from typing import Dict, List, Any

class CodeAnalyzer:
    def __init__(self, repo_url: str, output_dir: str):
        self.repo_url = repo_url
        self.output_dir = output_dir
        self.repo_name = repo_url.split('/')[-1].replace('.git', '')
        self.local_path = os.path.join('/tmp', self.repo_name)
        
    def clone_repository(self):
        """Clone the repository for analysis"""
        if os.path.exists(self.local_path):
            subprocess.run(['rm', '-rf', self.local_path], check=True)
        subprocess.run(['git', 'clone', '--depth=1', self.repo_url, self.local_path], check=True)
        
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze repository structure and extract components"""
        components = []
        dependencies = {}
        
        # Walk through the repository
        for root, dirs, files in os.walk(self.local_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.go', '.java', '.cpp', '.h')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.local_path)
                    
                    # Extract component info
                    component_info = self._extract_component_info(file_path, relative_path)
                    if component_info:
                        components.append(component_info)
                        
        return {
            'components': components,
            'dependencies': dependencies,
            'repo_info': {
                'url': self.repo_url,
                'name': self.repo_name
            }
        }
        
    def _extract_component_info(self, file_path: str, relative_path: str) -> Dict[str, Any]:
        """Extract component information from a source file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Basic metrics
            lines = len(content.split('\n'))
            imports = self._extract_imports(content, file_path)
            
            return {
                'file_path': relative_path,
                'lines_of_code': lines,
                'imports': imports,
                'complexity': self._estimate_complexity(content),
                'language': self._detect_language(file_path)
            }
        except Exception as e:
            return None
            
    def _extract_imports(self, content: str, file_path: str) -> List[str]:
        """Extract import statements from source code"""
        imports = []
        language = self._detect_language(file_path)
        
        if language == 'python':
            for line in content.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    imports.append(line.strip())
        elif language in ['javascript', 'typescript']:
            for line in content.split('\n'):
                if 'require(' in line or 'import ' in line:
                    imports.append(line.strip())
        # Add more languages as needed
        
        return imports
        
    def _estimate_complexity(self, content: str) -> int:
        """Estimate code complexity (simplified)"""
        # Count control flow statements as a proxy for complexity
        complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch']
        complexity = 0
        for keyword in complexity_keywords:
            complexity += content.count(keyword)
        return complexity
        
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'c++',
            '.cc': 'c++',
            '.cxx': 'c++',
            '.h': 'c-header',
            '.hpp': 'c-header'
        }
        return language_map.get(ext, 'unknown')
        
    def save_analysis(self, analysis_data: Dict[str, Any]):
        """Save analysis results to JSON file"""
        output_file = os.path.join(self.output_dir, 'data', 'code-analysis.json')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
    def run_full_analysis(self, repo_url: str = None):
        """Run complete code analysis pipeline"""
        if repo_url:
            self.repo_url = repo_url
            
        print(f"Starting code analysis for {self.repo_url}")
        self.clone_repository()
        analysis_data = self.analyze_structure()
        self.save_analysis(analysis_data)
        print(f"Analysis completed. Results saved to {self.output_dir}/data/code-analysis.json")
        
        return analysis_data

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) != 3:
        print("Usage: python code-analysis-module.py <repo_url> <output_dir>")
        sys.exit(1)
        
    repo_url = sys.argv[1]
    output_dir = sys.argv[2]
    
    analyzer = CodeAnalyzer(repo_url, output_dir)
    analyzer.run_full_analysis()