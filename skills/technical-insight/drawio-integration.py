#!/usr/bin/env python3
"""
DrawIO Integration Module for Technical Insight Skill
Generates draw.io compatible architecture diagrams alongside PlantUML diagrams
"""

import os
import json
from typing import Dict, Any

class DrawIOIntegration:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.diagrams_dir = os.path.join(output_dir, 'diagrams')
        os.makedirs(self.diagrams_dir, exist_ok=True)
        
    def generate_drawio_diagrams(self, analysis_data: Dict[str, Any]):
        """Generate draw.io compatible diagrams based on analysis data"""
        print("🎨 Generating draw.io compatible architecture diagrams...")
        
        system_name = analysis_data.get('repo_info', {}).get('name', 'System')
        
        # Generate architecture.drawio (System Context + High-level Architecture)
        self._create_architecture_drawio(system_name, analysis_data)
        
        # Generate component.drawio (Component Diagram)
        self._create_component_drawio(system_name, analysis_data)
        
        # Generate data-flow.drawio (Data Flow Diagram)  
        self._create_dataflow_drawio(system_name, analysis_data)
        
        # Generate sequence.drawio (Sequence Diagram)
        self._create_sequence_drawio(system_name, analysis_data)
        
        print(f"✅ All draw.io diagrams generated in {self.diagrams_dir}")
        
    def _create_architecture_drawio(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create system architecture diagram in draw.io format"""
        components = analysis_data.get('components', [])
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="system" value="{system_name}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="300" y="200" width="200" height="120" as="geometry"/>
    </mxCell>"""
        
        # Add key components as external systems
        external_systems = ["User", "Database", "External API", "Message Queue"]
        for i, system in enumerate(external_systems):
            if i < 2:  # Left side
                x, y = 100, 180 + i * 80
                mxgraph_content += f"""
    <mxCell id="ext_{i}" value="{system}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="edge_{i}" style="endArrow=none;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="ext_{i}" target="system">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="{x+120}" y="{y+30}" as="sourcePoint"/>
        <mxPoint x="{x+170}" y="{y-20}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            else:  # Right side
                x, y = 550, 180 + (i-2) * 80
                mxgraph_content += f"""
    <mxCell id="ext_{i}" value="{system}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="edge_{i}" style="endArrow=none;html=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="system" target="ext_{i}">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="{x-50}" y="{y+30}" as="sourcePoint"/>
        <mxPoint x="{x}" y="{y-20}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
                
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "architecture.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_component_drawio(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create component diagram in draw.io format"""
        components = analysis_data.get('components', [])[:8]  # Limit to 8 components
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="container" value="{system_name} Components" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="150" y="80" width="500" height="400" as="geometry"/>
    </mxCell>"""
        
        # Position components in a grid
        positions = [
            (200, 150), (300, 150), (400, 150), (500, 150),
            (200, 250), (300, 250), (400, 250), (500, 250)
        ]
        
        for i, comp in enumerate(components):
            x, y = positions[i]
            file_path = comp.get('file_path', f'Component_{i+1}')
            language = comp.get('language', 'unknown')
            
            # Extract component name from file path
            comp_name = file_path.split('/')[-1].replace('.py', '').replace('.md', '')
            
            mxgraph_content += f"""
    <mxCell id="comp_{i}" value="{comp_name}\\n{language}" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="80" height="60" as="geometry"/>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "component.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_dataflow_drawio(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create data flow diagram in draw.io format"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="user" value="User" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="100" y="250" width="30" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="api" value="API Layer" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="200" y="240" width="100" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="core" value="Core Engine" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="350" y="240" width="100" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="memory" value="Memory System" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="500" y="180" width="100" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="tools" value="Tool Integrator" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="500" y="300" width="100" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="db" value="Database" style="shape=datastore;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="650" y="240" width="60" height="60" as="geometry"/>
    </mxCell>"""
        
        # Add data flow connections
        connections = [
            ("user", "api", "Request"),
            ("api", "core", "Process"),
            ("core", "memory", "Store Context"),
            ("core", "tools", "Execute Tools"), 
            ("memory", "core", "Load Context"),
            ("tools", "db", "Data Access"),
            ("db", "core", "Return Data"),
            ("core", "api", "Response"),
            ("api", "user", "Result")
        ]
        
        for i, (source, target, label) in enumerate(connections):
            mxgraph_content += f"""
    <mxCell id="conn_{i}" value="{label}" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="{source}" target="{target}">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "data-flow.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_sequence_drawio(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create sequence diagram in draw.io format"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="user_lifeline" value="User" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;" vertex="1" parent="1">
      <mxGeometry x="120" y="80" width="20" height="320" as="geometry"/>
    </mxCell>
    <mxCell id="api_lifeline" value="API Layer" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;" vertex="1" parent="1">
      <mxGeometry x="220" y="80" width="20" height="320" as="geometry"/>
    </mxCell>
    <mxCell id="core_lifeline" value="Core Engine" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;" vertex="1" parent="1">
      <mxGeometry x="320" y="80" width="20" height="320" as="geometry"/>
    </mxCell>
    <mxCell id="memory_lifeline" value="Memory System" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;" vertex="1" parent="1">
      <mxGeometry x="420" y="80" width="20" height="320" as="geometry"/>
    </mxCell>"""
        
        # Add activation bars and messages
        activations = [
            ("user_lifeline", 100, 300),
            ("api_lifeline", 120, 280), 
            ("core_lifeline", 140, 260),
            ("memory_lifeline", 160, 200)
        ]
        
        for i, (lifeline, start_y, height) in enumerate(activations):
            mxgraph_content += f"""
    <mxCell id="activation_{i}" value="" style="html=1;points=[];perimeter=orthogonalPerimeter;" vertex="1" parent="1">
      <mxGeometry x="10" y="{start_y - 80}" width="10" height="{height}" as="geometry">
        <mxPoint x="-5" y="0" as="offset"/>
      </mxGeometry>
    </mxCell>"""
            
        # Add messages
        messages = [
            (120, "user_lifeline", "api_lifeline", "sendRequest()"),
            (140, "api_lifeline", "core_lifeline", "processInput()"),
            (160, "core_lifeline", "memory_lifeline", "getContext()"),
            (200, "memory_lifeline", "core_lifeline", "returnContext()"),
            (220, "core_lifeline", "api_lifeline", "generateResponse()"),
            (240, "api_lifeline", "user_lifeline", "returnResult()")
        ]
        
        for i, (y_pos, source, target, message) in enumerate(messages):
            mxgraph_content += f"""
    <mxCell id="message_{i}" value="{message}" style="html=1;verticalAlign=bottom;endArrow=block;exitX=1;exitY={((y_pos-80)/320)};exitDx=0;exitDy=0;entryX=0;entryY={((y_pos-80)/320)};entryDx=0;entryDy=0;" edge="1" parent="1" source="{source}" target="{target}">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="0" y="{y_pos}" as="sourcePoint"/>
        <mxPoint x="100" y="{y_pos}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "sequence.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python drawio-integration.py <analysis_data_path>")
        sys.exit(1)
        
    analysis_data_path = sys.argv[1]
    output_dir = os.path.dirname(os.path.dirname(analysis_data_path))
    
    # Load analysis data
    with open(analysis_data_path, 'r') as f:
        analysis_data = json.load(f)
        
    # Generate draw.io diagrams
    drawio_gen = DrawIOIntegration(output_dir)
    drawio_gen.generate_drawio_diagrams(analysis_data)