#!/usr/bin/env python3
"""
Professional Layered Architecture Diagram Generator v2
Generates numbered, professionally layered architecture diagrams in draw.io format
"""

import os
import json
from typing import Dict, Any

class LayeredArchitectureGeneratorV2:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.diagrams_dir = os.path.join(output_dir, 'diagrams')
        os.makedirs(self.diagrams_dir, exist_ok=True)
        
    def generate_numbered_diagrams(self, analysis_data: Dict[str, Any]):
        """Generate professionally numbered and layered architecture diagrams"""
        print("🎨 Generating professionally numbered layered architecture diagrams...")
        
        system_name = analysis_data.get('repo_info', {}).get('name', 'System')
        
        # 01 - System Context Diagram
        self._create_01_system_context(system_name, analysis_data)
        
        # 02 - Containers Diagram  
        self._create_02_containers(system_name, analysis_data)
        
        # 03 - Components Diagram
        self._create_03_components(system_name, analysis_data)
        
        # 04 - Data Flow Diagram
        self._create_04_data_flow(system_name, analysis_data)
        
        print(f"✅ All professionally numbered diagrams generated in {self.diagrams_dir}")
        
    def _create_01_system_context(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create 01-system-context.drawio with proper numbering and layers"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="01 - System Context Diagram" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>
    <mxCell id="system" value="{system_name}" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="300" y="200" width="200" height="120" as="geometry"/>
    </mxCell>"""
        
        # 01-external_users (Left side)
        mxgraph_content += """
    <mxCell id="01_external_users" value="01 - External Users" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="100" y="180" width="30" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="edge_01" style="endArrow=none;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="01_external_users" target="system">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="130" y="210" as="sourcePoint"/>
        <mxPoint x="180" y="160" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
        
        # 02-system_boundary (System itself)
        # Already created as the main system box
        
        # 03-external_systems (Right side)
        mxgraph_content += """
    <mxCell id="03_external_systems" value="03 - External Systems" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="550" y="180" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="edge_03" style="endArrow=none;html=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="system" target="03_external_systems">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="500" y="210" as="sourcePoint"/>
        <mxPoint x="550" y="160" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
                
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "01-system-context.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_02_containers(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create 02-containers.drawio with numbered layers"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="02 - Container Architecture" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>"""
        
        # 01-infrastructure layer (Bottom)
        mxgraph_content += """
    <mxCell id="01_infrastructure" value="01 - Infrastructure Layer\\nFile System, Network, Security" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#E3F2FD;" vertex="1" parent="1">
      <mxGeometry x="200" y="400" width="400" height="80" as="geometry"/>
    </mxCell>"""
        
        # 02-platform layer
        mxgraph_content += """
    <mxCell id="02_platform" value="02 - Platform Layer\\nMemory System, Tool Integrator, Skills Framework" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#BBDEFB;" vertex="1" parent="1">
      <mxGeometry x="200" y="300" width="400" height="80" as="geometry"/>
    </mxCell>"""
        
        # 03-application layer  
        mxgraph_content += """
    <mxCell id="03_application" value="03 - Application Layer\\nCore Engine, API Layer, Executor" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#90CAF9;" vertex="1" parent="1">
      <mxGeometry x="200" y="200" width="400" height="80" as="geometry"/>
    </mxCell>"""
        
        # 04-interface layer (Top)
        mxgraph_content += """
    <mxCell id="04_interface" value="04 - Interface Layer\\nUser Interaction, External APIs" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#64B5F6;" vertex="1" parent="1">
      <mxGeometry x="200" y="100" width="400" height="80" as="geometry"/>
    </mxCell>"""
        
        # Add dependency arrows (top-down flow)
        mxgraph_content += """
    <mxCell id="dep_04_to_03" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="04_interface" target="03_application">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="dep_03_to_02" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="03_application" target="02_platform">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="dep_02_to_01" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="02_platform" target="01_infrastructure">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "02-containers.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_03_components(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create 03-components.drawio with numbered component layers"""
        components = analysis_data.get('components', [])[:8]
        
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="03 - Component Architecture" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>"""
        
        # 01-presentation layer
        mxgraph_content += """
    <mxCell id="01_presentation" value="01 - Presentation Layer\\nInput Parser, Response Generator" style="ellipse;whiteSpace=wrap;html=1;fillColor=#FFEBEE;" vertex="1" parent="1">
      <mxGeometry x="350" y="120" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # 02-business_logic layer
        mxgraph_content += """
    <mxCell id="02_business_logic" value="02 - Business Logic Layer\\nIntent Matcher, Skill Router, Core Engine" style="ellipse;whiteSpace=wrap;html=1;fillColor=#FFCDD2;" vertex="1" parent="1">
      <mxGeometry x="350" y="220" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # 03-data_access layer
        mxgraph_content += """
    <mxCell id="03_data_access" value="03 - Data Access Layer\\nMemory Manager, Context Storage" style="ellipse;whiteSpace=wrap;html=1;fillColor=#EF9A9A;" vertex="1" parent="1">
      <mxGeometry x="250" y="320" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # 04-external_integration layer
        mxgraph_content += """
    <mxCell id="04_external_integration" value="04 - External Integration Layer\\nTool Integrator, API Client" style="ellipse;whiteSpace=wrap;html=1;fillColor=#E57373;" vertex="1" parent="1">
      <mxGeometry x="450" y="320" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # Dependency arrows
        mxgraph_content += """
    <mxCell id="dep_pres_to_logic" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="01_presentation" target="02_business_logic">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="dep_logic_to_data" style="endArrow=classic;html=1;exitX=0.25;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="02_business_logic" target="03_data_access">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="dep_logic_to_ext" style="endArrow=classic;html=1;exitX=0.75;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="02_business_logic" target="04_external_integration">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "03-components.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)
            
    def _create_04_data_flow(self, system_name: str, analysis_data: Dict[str, Any]):
        """Create 04-data-flow.drawio with numbered flow stages"""
        mxgraph_content = f"""<mxGraphModel dx="1426" dy="738" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="title" value="04 - Data Flow Diagram" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=18;fontStyle=1" vertex="1" parent="1">
      <mxGeometry x="350" y="40" width="200" height="30" as="geometry"/>
    </mxCell>"""
        
        # 01-input stage
        mxgraph_content += """
    <mxCell id="01_input" value="01 - Input Stage\\nUser Request, Natural Language" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E8;" vertex="1" parent="1">
      <mxGeometry x="100" y="250" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # 02-processing stage
        mxgraph_content += """
    <mxCell id="02_processing" value="02 - Processing Stage\\nIntent Recognition, Skill Routing" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#C8E6C9;" vertex="1" parent="1">
      <mxGeometry x="250" y="250" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # 03-storage stage
        mxgraph_content += """
    <mxCell id="03_storage" value="03 - Storage Stage\\nContext Management, Memory" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#A5D6A7;" vertex="1" parent="1">
      <mxGeometry x="400" y="200" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # 04-output stage
        mxgraph_content += """
    <mxCell id="04_output" value="04 - Output Stage\\nResponse Generation, Result Delivery" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#81C784;" vertex="1" parent="1">
      <mxGeometry x="550" y="250" width="120" height="80" as="geometry"/>
    </mxCell>"""
        
        # Data flow arrows
        mxgraph_content += """
    <mxCell id="flow_01_to_02" value="Parse & Analyze" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="01_input" target="02_processing">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="flow_02_to_03" value="Store Context" style="endArrow=classic;html=1;exitX=0.75;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;" edge="1" parent="1" source="02_processing" target="03_storage">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="flow_03_to_02" value="Load Context" style="endArrow=classic;html=1;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.25;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="03_storage" target="02_processing">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>
    <mxCell id="flow_02_to_04" value="Generate Response" style="endArrow=classic;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" parent="1" source="02_processing" target="04_output">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="0" y="0" as="sourcePoint"/>
        <mxPoint x="50" y="-50" as="targetPoint"/>
      </mxGeometry>
    </mxCell>"""
            
        mxgraph_content += """
  </root>
</mxGraphModel>"""
        
        diagram_path = os.path.join(self.diagrams_dir, "04-data-flow.drawio")
        with open(diagram_path, 'w') as f:
            f.write(mxgraph_content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python layered-architecture-generator-v2.py <analysis_data_path>")
        sys.exit(1)
        
    analysis_data_path = sys.argv[1]
    output_dir = os.path.dirname(os.path.dirname(analysis_data_path))
    
    with open(analysis_data_path, 'r') as f:
        analysis_data = json.load(f)
        
    generator = LayeredArchitectureGeneratorV2(output_dir)
    generator.generate_numbered_diagrams(analysis_data)