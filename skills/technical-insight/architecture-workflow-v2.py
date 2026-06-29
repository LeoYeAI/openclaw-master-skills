#!/usr/bin/env python3
"""
Architecture Analysis Workflow v2 - 5-Layer Architecture Implementation
Implements the complete 6-step workflow with 5-layer architecture model integration
"""

import os
import json
import subprocess
from typing import Dict, Any

class ArchitectureWorkflowV2:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.diagrams_dir = os.path.join(output_dir, 'diagrams')
        self.data_dir = os.path.join(output_dir, 'data')
        os.makedirs(self.diagrams_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
    def execute_complete_workflow(self, analysis_data: Dict[str, Any]):
        """Execute the complete 6-step architecture analysis workflow with 5-layer model"""
        print("🚀 Starting 5-Layer Architecture Analysis Workflow...")
        
        # Step 1: Analyze existing code and extract repeated logic
        print("1️⃣ Analyzing code structure and extracting patterns...")
        code_patterns = self._extract_code_patterns(analysis_data)
        
        # Step 2: Split modules by business boundaries  
        print("2️⃣ Identifying business boundaries and module splits...")
        business_modules = self._identify_business_modules(analysis_data)
        
        # Step 3: Define interfaces and dependencies
        print("3️⃣ Defining interfaces and dependency relationships...")
        interfaces_deps = self._define_interfaces_and_deps(analysis_data)
        
        # Step 4: Choose architectural layers and patterns
        print("4️⃣ Selecting 5-layer architecture strategy...")
        arch_patterns = self._select_five_layer_architecture(analysis_data)
        
        # Step 5: Make decisions around performance, availability, scalability
        print("5️⃣ Making performance, availability, and scalability decisions...")
        quality_decisions = self._make_quality_attribute_decisions(analysis_data)
        
        # Step 6: Generate 5-layer architecture diagrams using source-to-architecture skill
        print("6️⃣ Generating 5-Layer Architecture diagrams...")
        self._generate_five_layer_views(
            analysis_data, 
            code_patterns,
            business_modules,
            interfaces_deps, 
            arch_patterns,
            quality_decisions
        )
        
        print("✅ Complete 5-Layer Architecture workflow executed successfully!")
        
    def _extract_code_patterns(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 1: Extract repeated logic and code patterns"""
        components = analysis_data.get('components', [])
        
        # Identify common patterns
        patterns = {
            'error_handling': [],
            'logging': [],
            'validation': [],
            'caching': [],
            'authentication': []
        }
        
        for comp in components:
            file_path = comp.get('file_path', '')
            if 'error' in file_path.lower() or 'exception' in file_path.lower():
                patterns['error_handling'].append(comp)
            elif 'log' in file_path.lower():
                patterns['logging'].append(comp)
            elif 'validate' in file_path.lower() or 'validator' in file_path.lower():
                patterns['validation'].append(comp)
            elif 'cache' in file_path.lower():
                patterns['caching'].append(comp)
            elif 'auth' in file_path.lower() or 'security' in file_path.lower():
                patterns['authentication'].append(comp)
                
        return patterns
        
    def _identify_business_modules(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Identify business boundaries and create modules"""
        components = analysis_data.get('components', [])
        
        # Group by business domains (simplified heuristic)
        business_domains = {}
        for comp in components:
            file_path = comp.get('file_path', '')
            parts = file_path.split('/')
            
            # Use first directory level as business domain
            if len(parts) > 1:
                domain = parts[0]
                if domain not in business_domains:
                    business_domains[domain] = []
                business_domains[domain].append(comp)
            else:
                if 'core' not in business_domains:
                    business_domains['core'] = []
                business_domains['core'].append(comp)
                
        return business_domains
        
    def _define_interfaces_and_deps(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Define interfaces and dependencies between modules"""
        components = analysis_data.get('components', [])
        dependencies = analysis_data.get('dependencies', {})
        
        # Create interface definitions
        interfaces = {}
        for comp in components:
            file_path = comp.get('file_path', '')
            # Simplified interface extraction based on file naming
            if file_path.endswith(('api.py', 'interface.py', 'service.py')):
                module_name = file_path.replace('.py', '').replace('/', '.')
                interfaces[module_name] = {
                    'endpoints': [],  # Would be populated from actual code analysis
                    'dependencies': dependencies.get(file_path, []),
                    'consumers': []   # Would be reverse-engineered from dependencies
                }
                
        return {
            'interfaces': interfaces,
            'dependencies': dependencies
        }
        
    def _select_five_layer_architecture(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Select appropriate 5-layer architecture strategy"""
        components = analysis_data.get('components', [])
        
        # Map components to 5-layer architecture
        five_layers = {
            'access_layer': [],      # 接入层: API Gateway, Client, Web, App
            'control_layer': [],     # 路由/控制层: Controller, Service, Manager  
            'logic_layer': [],       # 逻辑层: Core, Logic, Executor
            'data_access_layer': [], # 数据访问层: DAO, Repository, Cache
            'storage_layer': []      # 存储/外部层: DB, MQ, Redis, 第三方服务
        }
        
        for comp in components:
            file_path = comp.get('file_path', '')
            file_name = file_path.split('/')[-1].lower()
            
            # 接入层识别
            if any(keyword in file_path.lower() for keyword in ['api', 'gateway', 'client', 'web', 'app', 'ui', 'frontend']):
                five_layers['access_layer'].append(comp)
            # 控制层识别  
            elif any(keyword in file_path.lower() for keyword in ['controller', 'service', 'manager', 'handler', 'router']):
                five_layers['control_layer'].append(comp)
            # 逻辑层识别
            elif any(keyword in file_path.lower() for keyword in ['core', 'logic', 'executor', 'engine', 'processor']):
                five_layers['logic_layer'].append(comp)
            # 数据访问层识别
            elif any(keyword in file_path.lower() for keyword in ['dao', 'repository', 'repo', 'cache', 'db', 'database']):
                five_layers['data_access_layer'].append(comp)
            # 存储层识别
            elif any(keyword in file_path.lower() for keyword in ['storage', 'external', 'third', 'mq', 'redis', 'kafka']):
                five_layers['storage_layer'].append(comp)
            else:
                # 默认归入逻辑层
                five_layers['logic_layer'].append(comp)
                
        return {
            'five_layer_mapping': five_layers,
            'layer_distribution': {layer: len(comps) for layer, comps in five_layers.items()}
        }
        
    def _make_quality_attribute_decisions(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Make decisions about performance, availability, scalability"""
        components = analysis_data.get('components', [])
        
        # Analyze quality attributes based on component characteristics
        quality_analysis = {
            'performance': {'bottlenecks': [], 'optimization_opportunities': []},
            'availability': {'single_points_of_failure': [], 'redundancy_opportunities': []},
            'scalability': {'horizontal_scaling_candidates': [], 'vertical_scaling_limits': []}
        }
        
        # Simple heuristics for quality attribute analysis
        for comp in components:
            complexity = comp.get('complexity', 0)
            lines_of_code = comp.get('lines_of_code', 0)
            
            if complexity > 10 or lines_of_code > 500:
                quality_analysis['performance']['bottlenecks'].append(comp)
                quality_analysis['scalability']['horizontal_scaling_candidates'].append(comp)
                
            # Add more sophisticated analysis as needed
            
        return quality_analysis
        
    def _generate_five_layer_views(self, analysis_data: Dict[str, Any], *args):
        """Step 6: Generate the complete 5-layer architecture diagrams using source-to-architecture skill"""
        # Save analysis data to temporary file for source-to-architecture skill
        temp_analysis_path = os.path.join(self.data_dir, "five-layer-analysis.json")
        with open(temp_analysis_path, 'w') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
        # Call the optimized source-to-architecture skill
        try:
            result = subprocess.run([
                'python3',
                '/home/Vincent/.openclaw/workspace/skills/source-to-architecture/scripts/drawio-generator.py',
                temp_analysis_path,
                self.diagrams_dir
            ], capture_output=True, text=True, check=True)
            
            print(f"✅ Source-to-Architecture skill executed successfully")
            print(f"📊 Output: {result.stdout}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error calling source-to-architecture skill: {e}")
            print(f".Stderr: {e.stderr}")
            # Fallback to basic generation if skill fails
            self._generate_basic_five_layer_diagram(analysis_data)
            
    def _generate_basic_five_layer_diagram(self, analysis_data: Dict[str, Any]):
        """Fallback basic 5-layer diagram generation"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="20" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="5-Layer Architecture" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="400" y="20" width="200" height="40" as="geometry"/>
    </mxCell>"""
        
        # 5 layers with proper spacing and colors
        layers = [
            ("接入层", "#ADD8E6", 100),      # 浅蓝
            ("控制层", "#4ECDC4", 200),      # 控制层用青色（原规范中没有明确，使用协调色）
            ("逻辑层", "#90EE90", 300),      # 浅绿  
            ("数据访问层", "#FFFFE0", 400),  # 浅黄
            ("存储层", "#E6E6FA", 500)       # 浅紫
        ]
        
        for layer_name, color, y_pos in layers:
            mxgraph_content += f"""
    <mxCell id="layer_{layer_name}" value="{layer_name}" style="swimlane;whiteSpace=wrap;html=1;startSize=26;fillColor={color};" vertex="1" parent="1">
      <mxGeometry x="200" y="{y_pos}" width="600" height="80" as="geometry"/>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "01-five-layer-architecture.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python architecture-workflow-v2.py <analysis_data_path>")
        sys.exit(1)
        
    analysis_data_path = sys.argv[1]
    output_dir = os.path.dirname(os.path.dirname(analysis_data_path))
    
    with open(analysis_data_path, 'r') as f:
        analysis_data = json.load(f)
        
    workflow = ArchitectureWorkflowV2(output_dir)
    workflow.execute_complete_workflow(analysis_data)