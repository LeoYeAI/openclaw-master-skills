#!/usr/bin/env python3
"""
Professional Layered Architecture Diagram Generator
Creates properly structured, hierarchical architecture diagrams following C4 model best practices
"""

import os
import json
from typing import Dict, List, Any

class LayeredArchitectureGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.diagrams_dir = os.path.join(output_dir, 'diagrams')
        os.makedirs(self.diagrams_dir, exist_ok=True)
        
    def create_layered_system_context(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create professional layered system context diagram"""
        # Extract system boundaries and external entities
        external_users = ["End User", "System Administrator"]
        external_systems = ["External APIs", "Database Systems", "Message Queues", "Monitoring Tools"]
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- System Boundary -->
    <mxCell id="system_boundary" value="" style="rounded=0;whiteSpace=wrap;html=1;dashed=1;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="300" y="150" width="500" height="400" as="geometry"/>
    </mxCell>
    <mxCell id="system_label" value="{system_name}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;" vertex="1" parent="1">
      <mxGeometry x="500" y="120" width="100" height="30" as="geometry"/>
    </mxCell>"""
        
        # Add internal system component (centered)
        mxgraph_content += f"""
    <mxCell id="internal_system" value="{system_name}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="475" y="300" width="150" height="100" as="geometry"/>
    </mxCell>"""
        
        # Add external users (left side - vertical alignment)
        user_y_positions = [200, 350]
        for i, user in enumerate(external_users):
            y_pos = user_y_positions[i]
            mxgraph_content += f"""
    <mxCell id="user_{i}" value="{user}" style="shape=actor;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="150" y="{y_pos}" width="40" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="user_edge_{i}" style="endArrow=none;html=1;strokeColor=#000000;" edge="1" parent="1" source="user_{i}" target="internal_system">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="190" y="{y_pos + 30}" as="sourcePoint"/>
        <mxPoint x="475" y="{y_pos + 30}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        # Add external systems (right side - vertical alignment)  
        system_y_positions = [180, 260, 340, 420]
        for i, system in enumerate(external_systems):
            y_pos = system_y_positions[i]
            mxgraph_content += f"""
    <mxCell id="ext_system_{i}" value="{system}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="850" y="{y_pos}" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="ext_edge_{i}" style="endArrow=none;html=1;strokeColor=#000000;" edge="1" parent="1" source="internal_system" target="ext_system_{i}">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="625" y="{y_pos + 30}" as="sourcePoint"/>
        <mxPoint x="850" y="{y_pos + 30}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "system-context.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
        return diagram_path
        
    def create_layered_container_diagram(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create professional layered container diagram with proper hierarchy"""
        components = analysis_data.get('components', [])
        
        # Categorize containers by layer
        presentation_layer = [
            {"name": "Web API", "tech": "Python/Flask", "desc": "REST API Interface"}
        ]
        application_layer = [
            {"name": "Core Engine", "tech": "Python", "desc": "Business Logic"},
            {"name": "Skills Manager", "tech": "Python", "desc": "Skill Orchestration"}
        ]
        infrastructure_layer = [
            {"name": "Memory System", "tech": "File System", "desc": "Context Storage"},
            {"name": "Tool Integrator", "tech": "Python", "desc": "External Tools"},
            {"name": "Security Module", "tech": "Python", "desc": "Access Control"}
        ]
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- System Boundary -->
    <mxCell id="system_boundary" value="" style="rounded=0;whiteSpace=wrap;html=1;dashed=1;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="100" y="100" width="900" height="600" as="geometry"/>
    </mxCell>
    <mxCell id="system_label" value="{system_name}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;" vertex="1" parent="1">
      <mxGeometry x="500" y="70" width="100" height="30" as="geometry"/>
    </mxCell>"""
        
        # Presentation Layer (Top)
        mxgraph_content += """
    <!-- Presentation Layer Label -->
    <mxCell id="presentation_label" value="Presentation Layer" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="50" y="150" width="120" height="30" as="geometry"/>
    </mxCell>"""
        
        # Web API Container
        mxgraph_content += """
    <mxCell id="web_api" value="Web API&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;Python/Flask&lt;/span&gt;&lt;br&gt;&lt;span style=&quot;font-size: 8px;&quot;&gt;REST API Interface&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
      <mxGeometry x="450" y="150" width="180" height="80" as="geometry"/>
    </mxCell>"""
        
        # Application Layer (Middle)
        mxgraph_content += """
    <!-- Application Layer Label -->
    <mxCell id="application_label" value="Application Layer" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="50" y="280" width="120" height="30" as="geometry"/>
    </mxCell>"""
        
        # Core Engine Container
        mxgraph_content += """
    <mxCell id="core_engine" value="Core Engine&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;Python&lt;/span&gt;&lt;br&gt;&lt;span style=&quot;font-size: 8px;&quot;&gt;Business Logic&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="350" y="280" width="180" height="80" as="geometry"/>
    </mxCell>"""
        
        # Skills Manager Container  
        mxgraph_content += """
    <mxCell id="skills_manager" value="Skills Manager&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;Python&lt;/span&gt;&lt;br&gt;&lt;span style=&quot;font-size: 8px;&quot;&gt;Skill Orchestration&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="580" y="280" width="180" height="80" as="geometry"/>
    </mxCell>"""
        
        # Infrastructure Layer (Bottom)
        mxgraph_content += """
    <!-- Infrastructure Layer Label -->
    <mxCell id="infrastructure_label" value="Infrastructure Layer" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="50" y="450" width="140" height="30" as="geometry"/>
    </mxCell>"""
        
        # Memory System Container
        mxgraph_content += """
    <mxCell id="memory_system" value="Memory System&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;File System&lt;/span&gt;&lt;br&gt;&lt;span style=&quot;font-size: 8px;&quot;&gt;Context Storage&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="250" y="450" width="160" height="80" as="geometry"/>
    </mxCell>"""
        
        # Tool Integrator Container
        mxgraph_content += """
    <mxCell id="tool_integrator" value="Tool Integrator&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;Python&lt;/span&gt;&lt;br&gt;&lt;span style=&quot;font-size: 8px;&quot;&gt;External Tools&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="450" y="450" width="160" height="80" as="geometry"/>
    </mxCell>"""
        
        # Security Module Container
        mxgraph_content += """
    <mxCell id="security_module" value="Security Module&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;Python&lt;/span&gt;&lt;br&gt;&lt;span style=&quot;font-size: 8px;&quot;&gt;Access Control&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="650" y="450" width="160" height="80" as="geometry"/>
    </mxCell>"""
        
        # Layer Connections (Vertical flow)
        connections = [
            ("web_api", "core_engine", "HTTP Requests"),
            ("core_engine", "memory_system", "Store/Load Context"), 
            ("core_engine", "tool_integrator", "Execute Tools"),
            ("skills_manager", "tool_integrator", "Skill Execution"),
            ("security_module", "core_engine", "AuthZ/AuthN")
        ]
        
        for i, (source, target, label) in enumerate(connections):
            mxgraph_content += f"""
    <mxCell id="conn_{i}" value="{label}" style="endArrow=classic;html=1;strokeColor=#000000;entryX=0.5;entryY=0;entryDx=0;entryDy=0;exitX=0.5;exitY=1;exitDx=0;exitDy=0;" edge="1" parent="1" source="{source}" target="{target}">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "containers.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
        return diagram_path
        
    def create_hierarchical_component_diagram(self, container_name: str, analysis_data: Dict[str, Any]):
        """Create hierarchical component diagram with proper nesting"""
        components = analysis_data.get('components', [])[:12]  # Limit to 12 components
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- Container Boundary -->
    <mxCell id="container_boundary" value="{container_name}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;" vertex="1" parent="1">
      <mxGeometry x="150" y="100" width="800" height="600" as="geometry"/>
    </mxCell>"""
        
        # Organize components into logical groups with proper hierarchy
        input_processing = []
        core_logic = []
        output_generation = []
        utilities = []
        
        for comp in components:
            file_path = comp.get('file_path', '')
            if 'input' in file_path.lower() or 'parse' in file_path.lower():
                input_processing.append(comp)
            elif 'core' in file_path.lower() or 'engine' in file_path.lower():
                core_logic.append(comp)
            elif 'output' in file_path.lower() or 'response' in file_path.lower():
                output_generation.append(comp)
            else:
                utilities.append(comp)
                
        # Limit each group to 3 components for clarity
        input_processing = input_processing[:3]
        core_logic = core_logic[:3] 
        output_generation = output_generation[:3]
        utilities = utilities[:3]
        
        # Input Processing Layer (Top)
        if input_processing:
            mxgraph_content += """
    <!-- Input Processing Group -->
    <mxCell id="input_group" value="Input Processing" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;" vertex="1" parent="1">
      <mxGeometry x="200" y="150" width="700" height="120" as="geometry"/>
    </mxCell>"""
            
            for i, comp in enumerate(input_processing):
                x = 250 + i * 200
                y = 180
                name = comp.get('file_path', '').split('/')[-1].replace('.py', '')
                tech = comp.get('language', 'Python')
                mxgraph_content += f"""
    <mxCell id="input_comp_{i}" value="{name}&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;{tech}&lt;/span&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="100" height="60" as="geometry"/>
    </mxCell>"""
                
        # Core Logic Layer (Middle)
        if core_logic:
            y_pos = 300 if input_processing else 150
            mxgraph_content += f"""
    <!-- Core Logic Group -->
    <mxCell id="core_group" value="Core Logic" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="200" y="{y_pos}" width="700" height="120" as="geometry"/>
    </mxCell>"""
            
            for i, comp in enumerate(core_logic):
                x = 250 + i * 200
                y = y_pos + 30
                name = comp.get('file_path', '').split('/')[-1].replace('.py', '')
                tech = comp.get('language', 'Python')
                mxgraph_content += f"""
    <mxCell id="core_comp_{i}" value="{name}&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;{tech}&lt;/span&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="100" height="60" as="geometry"/>
    </mxCell>"""
                
        # Output Generation Layer (Bottom)
        if output_generation:
            y_pos = 450 if (input_processing and core_logic) else (300 if core_logic else 150)
            mxgraph_content += f"""
    <!-- Output Generation Group -->
    <mxCell id="output_group" value="Output Generation" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="200" y="{y_pos}" width="700" height="120" as="geometry"/>
    </mxCell>"""
            
            for i, comp in enumerate(output_generation):
                x = 250 + i * 200
                y = y_pos + 30
                name = comp.get('file_path', '').split('/')[-1].replace('.py', '')
                tech = comp.get('language', 'Python')
                mxgraph_content += f"""
    <mxCell id="output_comp_{i}" value="{name}&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;{tech}&lt;/span&gt;" style="ellipse;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="100" height="60" as="geometry"/>
    </mxCell>"""
                
        # Utilities (Right side)
        if utilities:
            mxgraph_content += """
    <!-- Utilities Group -->
    <mxCell id="utils_group" value="Utilities" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;" vertex="1" parent="1">
      <mxGeometry x="850" y="300" width="100" height="120" as="geometry"/>
    </mxCell>"""
            
            for i, comp in enumerate(utilities):
                x = 870
                y = 330 + i * 30
                name = comp.get('file_path', '').split('/')[-1].replace('.py', '')[:15]  # Truncate long names
                tech = comp.get('language', 'Python')
                mxgraph_content += f"""
    <mxCell id="util_comp_{i}" value="{name}&lt;br&gt;&lt;span style=&quot;font-size: 8px;&quot;&gt;{tech}&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="{x}" y="{y}" width="60" height="25" as="geometry"/>
    </mxCell>"""
                
        # Data Flow Connections (Top to Bottom)
        if input_processing and core_logic:
            mxgraph_content += """
    <mxCell id="flow_1" style="endArrow=classic;html=1;strokeColor=#000000;" edge="1" parent="1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="500" y="270" as="sourcePoint"/>
        <mxPoint x="500" y="300" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        if core_logic and output_generation:
            core_y = 420 if input_processing else 270
            output_y = 450 if (input_processing and core_logic) else 300
            mxgraph_content += f"""
    <mxCell id="flow_2" style="endArrow=classic;html=1;strokeColor=#000000;" edge="1" parent="1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="500" y="{core_y}" as="sourcePoint"/>
        <mxPoint x="500" y="{output_y}" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "components.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
        return diagram_path
        
    def create_data_flow_hierarchy(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create hierarchical data flow diagram showing data movement through layers"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- External User -->
    <mxCell id="external_user" value="External User" style="shape=actor;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;" vertex="1" parent="1">
      <mxGeometry x="100" y="350" width="40" height="60" as="geometry"/>
    </mxCell>"""
        
        # Data Flow Layers (Left to Right)
        layers = [
            ("API Gateway", "Receives HTTP requests", 250),
            ("Input Parser", "Parses and validates input", 400), 
            ("Intent Matcher", "Identifies user intent", 550),
            ("Skill Router", "Routes to appropriate skill", 700),
            ("Executor", "Executes skill logic", 850),
            ("Response Generator", "Formats final response", 1000)
        ]
        
        for i, (name, desc, x_pos) in enumerate(layers):
            mxgraph_content += f"""
    <mxCell id="layer_{i}" value="{name}&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;{desc}&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;" vertex="1" parent="1">
      <mxGeometry x="{x_pos}" y="320" width="120" height="80" as="geometry"/>
    </mxCell>"""
            
        # Data Flow Arrows
        mxgraph_content += """
    <!-- Data Flow Arrows -->
    <mxCell id="flow_start" style="endArrow=classic;html=1;strokeColor=#000000;" edge="1" parent="1" source="external_user" target="layer_0">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="140" y="380" as="sourcePoint"/>
        <mxPoint x="250" y="380" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
        
        for i in range(len(layers) - 1):
            mxgraph_content += f"""
    <mxCell id="flow_{i}" style="endArrow=classic;html=1;strokeColor=#000000;" edge="1" parent="1" source="layer_{i}" target="layer_{i+1}">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="{layers[i][2] + 120}" y="360" as="sourcePoint"/>
        <mxPoint x="{layers[i+1][2]}" y="360" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        # Feedback Loop (Memory System)
        mxgraph_content += """
    <!-- Memory System (Below main flow) -->
    <mxCell id="memory_system" value="Memory System&lt;br&gt;&lt;span style=&quot;font-size: 10px;&quot;&gt;Persistent Storage&lt;/span&gt;" style="shape=datastore;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;" vertex="1" parent="1">
      <mxGeometry x="550" y="500" width="80" height="80" as="geometry"/>
    </mxCell>
    <!-- Read from Memory -->
    <mxCell id="memory_read" style="endArrow=classic;html=1;strokeColor=#000000;entryX=0.5;entryY=1;entryDx=0;entryDy=0;" edge="1" parent="1" source="memory_system" target="layer_3">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="590" y="500" as="sourcePoint"/>
        <mxPoint x="590" y="400" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <!-- Write to Memory -->
    <mxCell id="memory_write" style="endArrow=classic;html=1;strokeColor=#000000;exitX=0.5;exitY=1;exitDx=0;exitDy=0;" edge="1" parent="1" source="layer_4" target="memory_system">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="650" y="400" as="sourcePoint"/>
        <mxPoint x="650" y="500" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "data-flow.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
        return diagram_path
        
    def generate_professional_diagrams(self, analysis_data: Dict[str, Any]):
        """Generate all professional layered architecture diagrams"""
        print("🎨 Generating professional layered architecture diagrams...")
        
        system_name = analysis_data.get('repo_info', {}).get('name', 'System')
        
        # Generate all diagram types with proper layering and hierarchy
        self.create_layered_system_context(system_name, analysis_data)
        self.create_layered_container_diagram(system_name, analysis_data)
        self.create_hierarchical_component_diagram("Core Engine", analysis_data)
        self.create_data_flow_hierarchy(system_name, analysis_data)
        
        print(f"✅ All professional diagrams generated in {self.diagrams_dir}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python layered-architecture-generator.py <analysis_data_path>")
        sys.exit(1)
        
    analysis_data_path = sys.argv[1]
    output_dir = os.path.dirname(os.path.dirname(analysis_data_path))
    
    # Load analysis data
    with open(analysis_data_path, 'r') as f:
        analysis_data = json.load(f)
        
    # Generate professional diagrams
    layered_gen = LayeredArchitectureGenerator(output_dir)
    layered_gen.generate_professional_diagrams(analysis_data)