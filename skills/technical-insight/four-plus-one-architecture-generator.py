#!/usr/bin/env python3
"""
4+1 View Architecture Diagram Generator
Implements the industrial standard 4+1 view model for software architecture documentation
"""

import os
import json
from typing import Dict, Any

class FourPlusOneArchitectureGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.diagrams_dir = os.path.join(output_dir, 'diagrams')
        os.makedirs(self.diagrams_dir, exist_ok=True)
        
    def generate_four_plus_one_diagrams(self, analysis_data: Dict[str, Any]):
        """Generate the complete 4+1 view architecture diagrams"""
        print("🎨 Generating 4+1 View Model architecture diagrams...")
        
        system_name = analysis_data.get('repo_info', {}).get('name', 'System')
        
        # Logical View (功能视图) - What the system does
        self._create_logical_view(system_name, analysis_data)
        
        # Development View (开发视图) - Code structure and organization  
        self._create_development_view(system_name, analysis_data)
        
        # Process View (进程视图) - Runtime behavior and concurrency
        self._create_process_view(system_name, analysis_data)
        
        # Physical View (物理视图) - Deployment and infrastructure
        self._create_physical_view(system_name, analysis_data)
        
        # Scenarios View (场景视图) - Use cases and workflows that tie everything together
        self._create_scenarios_view(system_name, analysis_data)
        
        print(f"✅ All 4+1 View Model diagrams generated in {self.diagrams_dir}")
        
    def _create_logical_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Logical View diagram showing functional components and relationships"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="Logical View - Functional Architecture" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>
    <mxCell id="subtitle" value="Shows WHAT the system does - functional components and their relationships" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="350" y="70" width="200" height="20" as="geometry"/>
    </mxCell>"""
        
        # Extract functional components from analysis data
        components = analysis_data.get('components', [])
        functional_components = []
        
        # Group by functional areas
        for comp in components[:6]:  # Limit to top 6 components
            file_path = comp.get('file_path', '')
            if any(keyword in file_path.lower() for keyword in ['api', 'service', 'handler', 'controller']):
                functional_components.append(('Business Logic', comp))
            elif any(keyword in file_path.lower() for keyword in ['db', 'database', 'storage', 'repo']):
                functional_components.append(('Data Access', comp))
            elif any(keyword in file_path.lower() for keyword in ['ui', 'view', 'presentation', 'frontend']):
                functional_components.append(('Presentation', comp))
            else:
                functional_components.append(('Utility', comp))
                
        # Create functional layers
        y_positions = {'Presentation': 150, 'Business Logic': 250, 'Data Access': 350, 'Utility': 450}
        
        for layer_name, y_pos in y_positions.items():
            layer_components = [comp for comp_type, comp in functional_components if comp_type == layer_name]
            if layer_components:
                mxgraph_content += f"""
    <mxCell id="layer_{layer_name.replace(' ', '_')}" value="{layer_name}" style="swimlane;whiteSpace=wrap;html=1;startSize=20;horizontal=1;" vertex="1" parent="1">
      <mxGeometry x="200" y="{y_pos}" width="400" height="80" as="geometry"/>
    </mxCell>"""
                
                # Add individual components within each layer
                for i, (_, comp) in enumerate(layer_components[:2]):  # Max 2 per layer
                    comp_name = comp.get('file_path', '').split('/')[-1].replace('.py', '').replace('.md', '')
                    mxgraph_content += f"""
    <mxCell id="comp_{layer_name.replace(' ', '_')}_{i}" value="{comp_name}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="layer_{layer_name.replace(' ', '_')}">
      <mxGeometry x="{100 + i * 150}" y="30" width="120" height="40" as="geometry"/>
    </mxCell>"""
        
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "01-logical-view.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_development_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Development View diagram showing code structure and modules"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="Development View - Code Structure" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>
    <mxCell id="subtitle" value="Shows HOW the system is built - code organization and module structure" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="350" y="70" width="200" height="20" as="geometry"/>
    </mxCell>"""
        
        # Create main system container
        mxgraph_content += f"""
    <mxCell id="system" value="{system_name}" style="swimlane;whiteSpace=wrap;html=1;startSize=30;horizontal=1;" vertex="1" parent="1">
      <mxGeometry x="150" y="120" width="500" height="400" as="geometry"/>
    </mxCell>"""
        
        # Extract directory structure from components
        directories = {}
        for comp in analysis_data.get('components', [])[:12]:
            file_path = comp.get('file_path', '')
            parts = file_path.split('/')
            if len(parts) > 1:
                dir_name = parts[0]
                if dir_name not in directories:
                    directories[dir_name] = []
                directories[dir_name].append(comp)
                
        # Position directories in a grid
        dir_names = list(directories.keys())[:4]
        positions = [(200, 180), (350, 180), (200, 300), (350, 300)]
        
        for i, dir_name in enumerate(dir_names):
            x, y = positions[i]
            file_count = len(directories[dir_name])
            mxgraph_content += f"""
    <mxCell id="dir_{dir_name}" value="{dir_name}\\n{file_count} files" style="folder;tabWidth=40;tabHeight=14;tabPosition=left;html=1;whiteSpace=wrap;" vertex="1" parent="system">
      <mxGeometry x="{x - 150}" y="{y - 120}" width="120" height="80" as="geometry"/>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "02-development-view.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_process_view(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create Process View diagram showing runtime processes and concurrency"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="Process View - Runtime Behavior" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>
    <mxCell id="subtitle" value="Shows HOW the system runs - processes, threads, and concurrency" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="350" y="70" width="200" height="20" as="geometry"/>
    </mxCell>"""
        
        # Main process
        mxgraph_content += """
    <mxCell id="main_process" value="Main Process\\n(API Server)" style="process;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="350" y="150" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # Worker processes
        mxgraph_content += """
    <mxCell id="worker_1" value="Worker Process 1\\n(Skill Executor)" style="process;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="200" y="280" width="120" height="80" as="geometry"/>
    </mxCell>
    <mxCell id="worker_2" value="Worker Process 2\\n(Memory Manager)" style="process;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="350" y="280" width="120" height="80" as="geometry"/>
    </mxCell>
    <mxCell id="worker_3" value="Worker Process 3\\n(Tool Integrator)" style="process;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="500" y="280" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # Communication flows
        mxgraph_content += """
    <mxCell id="flow_1" value="Request" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="main_process" target="worker_2">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="flow_2" value="Execute" style="endArrow=classic;html=1;exitX=0.25;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="main_process" target="worker_1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="flow_3" value="Tools" style="endArrow=classic;html=1;exitX=0.75;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="main_process" target="worker_3">
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
        """Create Physical View diagram showing deployment and infrastructure"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="Physical View - Deployment Architecture" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>
    <mxCell id="subtitle" value="Shows WHERE the system runs - deployment nodes and infrastructure" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="350" y="70" width="200" height="20" as="geometry"/>
    </mxCell>"""
        
        # Cloud infrastructure
        mxgraph_content += """
    <mxCell id="cloud" value="Cloud Infrastructure" style="shape=mxgraph.aws3.cloud;html=1;pointerEvents=1;dashed=0;fillColor=#F58536;gradientColor=none;strokeColor=#ffffff;aspect=fixed;" vertex="1" parent="1">
      <mxGeometry x="300" y="150" width="200" height="170" as="geometry"/>
    </mxCell>"""
        
        # Application servers
        mxgraph_content += """
    <mxCell id="app_server_1" value="Application Server 1" style="shape=server;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="220" y="220" width="60" height="80" as="geometry"/>
    </mxCell>
    <mxCell id="app_server_2" value="Application Server 2" style="shape=server;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="320" y="220" width="60" height="80" as="geometry"/>
    </mxCell>
    <mxCell id="app_server_3" value="Application Server 3" style="shape=server;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="420" y="220" width="60" height="80" as="geometry"/>
    </mxCell>"""
        
        # Database
        mxgraph_content += """
    <mxCell id="database" value="Database Cluster" style="shape=datastore;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="320" y="350" width="60" height="60" as="geometry"/>
    </mxCell>"""
        
        # External connections
        mxgraph_content += """
    <mxCell id="user" value="End User" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="100" y="250" width="30" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="external_api" value="External APIs" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="550" y="250" width="100" height="60" as="geometry"/>
    </mxCell>"""
        
        # Network connections
        mxgraph_content += """
    <mxCell id="user_to_cloud" style="endArrow=none;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="user" target="cloud">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="cloud_to_external" style="endArrow=none;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="cloud" target="external_api">
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
        """Create Scenarios View diagram showing key use cases and workflows"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="Scenarios View - Key Workflows" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>
    <mxCell id="subtitle" value="Shows HOW everything works together - key use cases and user stories" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=12;" vertex="1" parent="1">
      <mxGeometry x="350" y="70" width="200" height="20" as="geometry"/>
    </mxCell>"""
        
        # User actor
        mxgraph_content += """
    <mxCell id="user" value="User" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="100" y="250" width="30" height="60" as="geometry"/>
    </mxCell>"""
        
        # System boundary
        mxgraph_content += f"""
    <mxCell id="system_boundary" value="{system_name}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="200" y="150" width="400" height="250" as="geometry"/>
    </mxCell>"""
        
        # Key components inside system
        mxgraph_content += """
    <mxCell id="input_parser" value="Input Parser" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="system_boundary">
      <mxGeometry x="50" y="50" width="80" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="skill_router" value="Skill Router" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="system_boundary">
      <mxGeometry x="150" y="50" width="80" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="core_engine" value="Core Engine" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="system_boundary">
      <mxGeometry x="250" y="50" width="80" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="memory_system" value="Memory System" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="system_boundary">
      <mxGeometry x="150" y="130" width="80" height="60" as="geometry"/>
    </mxCell>"""
        
        # Workflow arrows
        mxgraph_content += """
    <mxCell id="step1" value="1. Parse Request" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="user" target="input_parser">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="step2" value="2. Route Skill" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="input_parser" target="skill_router">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="step3" value="3. Execute Core" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="skill_router" target="core_engine">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="step4" value="4. Load Context" style="endArrow=classic;html=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="skill_router" target="memory_system">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="step5" value="5. Return Result" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="core_engine" target="user">
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
        print("Usage: python four-plus-one-architecture-generator.py <analysis_data_path>")
        sys.exit(1)
        
    analysis_data_path = sys.argv[1]
    output_dir = os.path.dirname(os.path.dirname(analysis_data_path))
    
    with open(analysis_data_path, 'r') as f:
        analysis_data = json.load(f)
        
    generator = FourPlusOneArchitectureGenerator(output_dir)
    generator.generate_four_plus_one_diagrams(analysis_data)