#!/usr/bin/env python3
"""
Simple executable workflow for 4+1 View Architecture Analysis
Follows the exact steps: code analysis → module extraction → interface definition → layering → quality decisions → diagram generation
"""

import os
import json
from typing import Dict, List, Any

class FourPlusOneWorkflow:
    def __init__(self, repo_url: str, output_dir: str):
        self.repo_url = repo_url
        self.output_dir = output_dir
        self.analysis_data = None
        
    def step_1_extract_logic(self):
        """Step 1: Analyze existing code and extract repeated logic"""
        print("🔍 Step 1: Extracting repeated logic from code...")
        # Use existing code analysis module
        from code_analysis_module import CodeAnalyzer
        analyzer = CodeAnalyzer(self.repo_url, self.output_dir)
        self.analysis_data = analyzer.run_full_analysis()
        print("✅ Repeated logic extracted and analyzed")
        
    def step_2_module_splitting(self):
        """Step 2: Split modules by business boundaries"""
        print("🧩 Step 2: Splitting modules by business boundaries...")
        if not self.analysis_data:
            raise ValueError("Analysis data not available. Run step 1 first.")
            
        # Group components by business domains
        business_modules = self._group_by_business_boundary(self.analysis_data['components'])
        self.analysis_data['business_modules'] = business_modules
        print(f"✅ Identified {len(business_modules)} business modules")
        
    def step_3_define_interfaces(self):
        """Step 3: Define interfaces and dependencies"""
        print("🔌 Step 3: Defining interfaces and dependencies...")
        if 'business_modules' not in self.analysis_data:
            raise ValueError("Business modules not available. Run step 2 first.")
            
        interfaces = self._extract_interfaces(self.analysis_data['business_modules'])
        dependencies = self._analyze_dependencies(self.analysis_data['components'])
        self.analysis_data['interfaces'] = interfaces
        self.analysis_data['dependencies'] = dependencies
        print(f"✅ Defined {len(interfaces)} interfaces and {len(dependencies)} dependencies")
        
    def step_4_choose_patterns(self):
        """Step 4: Choose layering and architectural patterns"""
        print("🏗️ Step 4: Choosing layering and architectural patterns...")
        patterns = {
            'layering': 'Clean Architecture',
            'microservices': False,
            'event_driven': True,
            'api_gateway': True
        }
        self.analysis_data['architectural_patterns'] = patterns
        print(f"✅ Selected patterns: {patterns}")
        
    def step_5_quality_decisions(self):
        """Step 5: Make decisions around performance, availability, and scalability"""
        print("🎯 Step 5: Making quality attribute decisions...")
        quality_decisions = {
            'performance': {
                'caching_strategy': 'Redis + Local Cache',
                'database_optimization': 'Read replicas + Connection pooling',
                'async_processing': 'Message queue for heavy operations'
            },
            'availability': {
                'health_checks': 'Comprehensive endpoint monitoring',
                'circuit_breakers': 'Hystrix pattern for external calls',
                'graceful_degradation': 'Fallback mechanisms for non-critical features'
            },
            'scalability': {
                'horizontal_scaling': 'Stateless services with load balancing',
                'database_sharding': 'Future consideration based on growth',
                'cdn_integration': 'Static assets via CDN'
            }
        }
        self.analysis_data['quality_decisions'] = quality_decisions
        print("✅ Quality attribute decisions documented")
        
    def step_6_generate_diagrams(self):
        """Step 6: Generate 4+1 view architecture diagrams"""
        print("🎨 Step 6: Generating 4+1 view architecture diagrams...")
        from four_plus_one_architecture_generator import FourPlusOneGenerator
        generator = FourPlusOneGenerator(self.output_dir)
        generator.generate_four_plus_one_views(self.analysis_data)
        print("✅ All 4+1 view diagrams generated")
        
    def run_complete_workflow(self):
        """Execute the complete 6-step workflow"""
        print("🚀 Starting complete 4+1 view architecture analysis workflow...")
        
        self.step_1_extract_logic()
        self.step_2_module_splitting()
        self.step_3_define_interfaces()
        self.step_4_choose_patterns()
        self.step_5_quality_decisions()
        self.step_6_generate_diagrams()
        
        print("🎉 Complete 4+1 view architecture analysis finished!")
        return self.analysis_data
        
    def _group_by_business_boundary(self, components: List[Dict]) -> Dict[str, List[Dict]]:
        """Group components by business boundaries"""
        modules = {}
        for comp in components:
            file_path = comp['file_path']
            # Simple heuristic: group by top-level directory
            if '/' in file_path:
                module_name = file_path.split('/')[0]
            else:
                module_name = 'core'
                
            if module_name not in modules:
                modules[module_name] = []
            modules[module_name].append(comp)
            
        return modules
        
    def _extract_interfaces(self, business_modules: Dict[str, List[Dict]]) -> List[Dict]:
        """Extract public interfaces from business modules"""
        interfaces = []
        for module_name, components in business_modules.items():
            # Find components that likely contain public APIs
            for comp in components:
                if 'api' in comp['file_path'].lower() or 'service' in comp['file_path'].lower():
                    interfaces.append({
                        'module': module_name,
                        'component': comp['file_path'],
                        'type': 'REST API' if '.py' in comp['file_path'] else 'Library Interface'
                    })
        return interfaces
        
    def _analyze_dependencies(self, components: List[Dict]) -> List[Dict]:
        """Analyze dependencies between components"""
        dependencies = []
        for comp in components:
            imports = comp.get('imports', [])
            for imp in imports:
                # Simple dependency mapping
                if 'internal' in imp or comp['file_path'] in imp:
                    dependencies.append({
                        'source': comp['file_path'],
                        'target': imp,
                        'type': 'import'
                    })
        return dependencies

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python architecture-workflow.py <repo_url> <output_dir>")
        sys.exit(1)
        
    repo_url = sys.argv[1]
    output_dir = sys.argv[2]
    
    workflow = FourPlusOneWorkflow(repo_url, output_dir)
    workflow.run_complete_workflow()