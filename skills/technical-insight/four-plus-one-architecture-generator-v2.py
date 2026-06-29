#!/usr/bin/env python3
"""
4+1 View Architecture Diagram Generator
Generates professional architecture diagrams following the 4+1 view model standard
"""

import os
import json
from typing import Dict, Any

class FourPlusOneArchitectureGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.diagrams_dir = os.path.join(output_dir, 'diagrams')
        os.makedirs(self.diagrams_dir, exist_ok=True)
        
    def generate_four_plus_one_views(self, analysis_data: Dict[str, Any]):
        """Generate all 5 views of the 4+1 architecture model"""
        print("🎨 Generating 4+1 View Architecture Diagrams...")
        
        system_name = analysis_data.get('repo_info', {}).get('name', 'System')
        
        # 1. Logical View (功能视图)
        self._create_logical_view(system_name, analysis_data)
        
        # 2. Development View (开发视图) 
        self._create_development_view(system_name, analysis_data)
        
        # 3. Process View (进程视图)
        self._create_process_view(system_name, analysis_data)
        
        # 4. Physical View (物理视图)
        self._create_physical_view(system_name, analysis_data)
        
        # 5. Scenarios View (场景视图)
        self._create_scenarios_view(system_name, analysis_data)
        
        print(f"✅ All 4+1 View diagrams generated in {self.diagrams_dir}")
        
    def _create_logical_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Logical View - Functional decomposition and interfaces"""
        components = analysis_data.get('components', [])
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="逻辑视图 (Logical View)\\n功能模块分解与接口定义" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="300" y="40" width="300" height="40" as="geometry"/>
    </mxCell>
    <mxCell id="system_boundary" value="{system_name}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#E3F2FD;" vertex="1" parent="1">
      <mxGeometry x="150" y="120" width="500" height="400" as="geometry"/>
    </mxCell>"""
        
        # Extract functional modules from components
        functional_modules = []
        for comp in components[:6]:  # Limit to top 6 components
            file_path = comp.get('file_path', '')
            if any(keyword in file_path.lower() for keyword in ['handler', 'service', 'manager', 'controller']):
                module_name = file_path.split('/')[-1].replace('.py', '').replace('.go', '')
                functional_modules.append({
                    'name': module_name,
                    'language': comp.get('language', 'unknown'),
                    'complexity': comp.get('complexity', 0)
                })
                
        if not functional_modules:
            # Fallback to generic modules
            functional_modules = [
                {'name': '核心引擎', 'language': 'Go', 'complexity': 8},
                {'name': '技能路由器', 'language': 'Python', 'complexity': 6},
                {'name': '记忆管理器', 'language': 'Python', 'complexity': 5},
                {'name': '工具集成器', 'language': 'Python', 'complexity': 7}
            ]
            
        # Position modules in a grid within system boundary
        positions = [(200, 200), (350, 200), (500, 200), (200, 320), (350, 320), (500, 320)]
        for i, module in enumerate(functional_modules[:6]):
            x, y = positions[i]
            mxgraph_content += f"""
    <mxCell id="module_{i}" value="{module['name']}\\n{module['language']}" style="ellipse;whiteSpace=wrap;html=1;fillColor=#BBDEFB;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="100" height="60" as="geometry"/>
    </mxCell>"""
            
        # Add external interfaces
        mxgraph_content += """
    <mxCell id="external_user" value="外部用户" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="80" y="250" width="30" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="external_system" value="外部系统" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#FFCDD2;" vertex="1" parent="1">
      <mxGeometry x="680" y="250" width="100" height="60" as="geometry"/>
    </mxCell>"""
        
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "01-logical-view.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_development_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Development View - Code structure and dependencies"""
        components = analysis_data.get('components', [])
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="开发视图 (Development View)\\n代码结构与依赖关系" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="300" y="40" width="300" height="40" as="geometry"/>
    </mxCell>"""
        
        # Group components by directory/package
        package_groups = {}
        for comp in components[:12]:  # Limit to first 12 components
            file_path = comp.get('file_path', '')
            parts = file_path.split('/')
            if len(parts) > 1:
                package = parts[0]
                if package not in package_groups:
                    package_groups[package] = []
                package_groups[package].append(comp)
            else:
                if 'root' not in package_groups:
                    package_groups['root'] = []
                package_groups['root'].append(comp)
                
        # Create package containers
        y_pos = 150
        for package_name, comps in list(package_groups.items())[:4]:  # Limit to 4 packages
            mxgraph_content += f"""
    <mxCell id="package_{package_name}" value="{package_name}" style="swimlane;whiteSpace=wrap;html=1;fillColor=#E8F5E8;" vertex="1" parent="1">
      <mxGeometry x="200" y="{y_pos}" width="400" height="120" as="geometry"/>
    </mxCell>"""
            
            # Add files within package
            x_offset = 220
            for i, comp in enumerate(comps[:3]):  # Limit to 3 files per package
                file_name = comp.get('file_path', '').split('/')[-1]
                language = comp.get('language', 'unknown')
                mxgraph_content += f"""
    <mxCell id="file_{package_name}_{i}" value="{file_name}\\n{language}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#C8E6C9;" vertex="1" parent="1">
      <mxGeometry x="{x_offset + i * 120}" y="{y_pos + 30}" width="100" height="60" as="geometry"/>
    </mxCell>"""
                
            y_pos += 140
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "02-development-view.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_process_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Process View - Runtime behavior and concurrency"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="进程视图 (Process View)\\n运行时行为与并发模型" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="300" y="40" width="300" height="40" as="geometry"/>
    </mxCell>"""
        
        # Main process
        mxgraph_content += """
    <mxCell id="main_process" value="主进程\\nCore Engine" style="shape=process;whiteSpace=wrap;html=1;fillColor=#FFEBEE;" vertex="1" parent="1">
      <mxGeometry x="350" y="150" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # Worker processes/threads
        worker_processes = [
            ("技能执行器", "Skill Executor"),
            ("记忆管理器", "Memory Manager"), 
            ("工具集成器", "Tool Integrator"),
            ("API处理器", "API Handler")
        ]
        
        for i, (name_cn, name_en) in enumerate(worker_processes):
            x = 200 + i * 150
            y = 280
            mxgraph_content += f"""
    <mxCell id="worker_{i}" value="{name_cn}\\n{name_en}" style="shape=process;whiteSpace=wrap;html=1;fillColor=#FFCDD2;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="120" height="60" as="geometry"/>
    </mxCell>"""
            
        # Communication channels
        mxgraph_content += """
    <mxCell id="comm_1" value="请求队列" style="endArrow=none;html=1;exitX=0.25;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="main_process" target="worker_0">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="comm_2" value="上下文数据" style="endArrow=none;html=1;exitX=0.4;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="main_process" target="worker_1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="comm_3" value="工具调用" style="endArrow=none;html=1;exitX=0.6;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="main_process" target="worker_2">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="comm_4" value="API响应" style="endArrow=none;html=1;exitX=0.75;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="main_process" target="worker_3">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "03-process-view.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_physical_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Physical View - Deployment and infrastructure"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="物理视图 (Physical View)\\n部署架构与基础设施" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="300" y="40" width="300" height="40" as="geometry"/>
    </mxCell>"""
        
        # Cloud/Data Center
        mxgraph_content += """
    <mxCell id="cloud" value="云平台/数据中心" style="shape=cloud;whiteSpace=wrap;html=1;fillColor=#E3F2FD;" vertex="1" parent="1">
      <mxGeometry x="100" y="150" width="600" height="300" as="geometry"/>
    </mxCell>"""
        
        # Servers/Nodes
        nodes = [
            ("应用服务器", "Application Server"),
            ("数据库服务器", "Database Server"), 
            ("缓存服务器", "Cache Server"),
            ("消息队列", "Message Queue")
        ]
        
        for i, (name_cn, name_en) in enumerate(nodes):
            x = 150 + (i % 2) * 250
            y = 200 + (i // 2) * 120
            mxgraph_content += f"""
    <mxCell id="node_{i}" value="{name_cn}\\n{name_en}" style="shape=server;whiteSpace=wrap;html=1;fillColor=#BBDEFB;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="180" height="80" as="geometry"/>
    </mxCell>"""
            
        # Network connections
        mxgraph_content += """
    <mxCell id="network_1" value="内部网络" style="endArrow=none;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="node_0" target="node_1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="network_2" value="缓存连接" style="endArrow=none;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="node_0" target="node_2">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="network_3" value="消息总线" style="endArrow=none;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="node_0" target="node_3">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        # External user
        mxgraph_content += """
    <mxCell id="external_user" value="外部用户" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="50" y="250" width="30" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="internet" value="互联网" style="endArrow=none;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="external_user" target="cloud">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "04-physical-view.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_scenarios_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Scenarios View - Use case driven scenarios"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="场景视图 (Scenarios View)\\n关键用例端到端流程" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="300" y="40" width="300" height="40" as="geometry"/>
    </mxCell>"""
        
        # Key scenario: User request processing
        mxgraph_content += """
    <mxCell id="user" value="用户" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="100" y="250" width="30" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="api_gateway" value="API网关" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E8;" vertex="1" parent="1">
      <mxGeometry x="200" y="240" width="100" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="core_engine" value="核心引擎" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#C8E6C9;" vertex="1" parent="1">
      <mxGeometry x="350" y="240" width="100" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="skill_router" value="技能路由器" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#A5D6A7;" vertex="1" parent="1">
      <mxGeometry x="500" y="200" width="100" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="memory_system" value="记忆系统" style="shape=datastore;whiteSpace=wrap;html=1;fillColor=#81C784;" vertex="1" parent="1">
      <mxGeometry x="500" y="300" width="60" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="tool_executor" value="工具执行器" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#4CAF50;" vertex="1" parent="1">
      <mxGeometry x="650" y="240" width="100" height="60" as="geometry"/>
    </mxCell>"""
        
        # Scenario flow
        scenario_steps = [
            ("user", "api_gateway", "发送请求"),
            ("api_gateway", "core_engine", "解析意图"),
            ("core_engine", "skill_router", "路由技能"),
            ("core_engine", "memory_system", "加载上下文"),
            ("memory_system", "core_engine", "返回上下文"),
            ("skill_router", "tool_executor", "执行工具"),
            ("tool_executor", "core_engine", "返回结果"),
            ("core_engine", "api_gateway", "生成响应"),
            ("api_gateway", "user", "返回结果")
        ]
        
        for i, (source, target, label) in enumerate(scenario_steps):
            mxgraph_content += f"""
    <mxCell id="scenario_{i}" value="{label}" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="{source}" target="{target}">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "05-scenarios-view.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python four-plus-one-architecture-generator-v2.py <analysis_data_path>")
        sys.exit(1)
        
    analysis_data_path = sys.argv[1]
    output_dir = os.path.dirname(os.path.dirname(analysis_data_path))
    
    with open(analysis_data_path, 'r') as f:
        analysis_data = json.load(f)
        
    generator = FourPlusOneArchitectureGenerator(output_dir)
    generator.generate_four_plus_one_views(analysis_data)