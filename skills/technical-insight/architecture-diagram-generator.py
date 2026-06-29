#!/usr/bin/env python3
"""
Architecture Diagram Generator for Technical Insight Skill
Generates various types of architecture diagrams from code analysis data
"""

import os
import json
import subprocess
from typing import Dict, List, Any

class ArchitectureDiagramGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.diagrams_dir = os.path.join(output_dir, 'diagrams')
        os.makedirs(self.diagrams_dir, exist_ok=True)
        
    def generate_component_diagram(self, analysis_data: Dict[str, Any]):
        """Generate component diagram showing system components and relationships"""
        components = analysis_data.get('components', [])
        dependencies = analysis_data.get('dependencies', {})
        
        # Create PlantUML component diagram
        plantuml_content = "@startuml\n"
        plantuml_content += "title System Component Diagram\n\n"
        
        # Group components by directory/module
        component_groups = {}
        for comp in components:
            file_path = comp['file_path']
            parts = file_path.split('/')
            if len(parts) > 1:
                group = parts[0]
                if group not in component_groups:
                    component_groups[group] = []
                component_groups[group].append(comp)
            else:
                if 'root' not in component_groups:
                    component_groups['root'] = []
                component_groups['root'].append(comp)
                
        # Create packages for each group
        for group_name, group_components in component_groups.items():
            plantuml_content += f"package \"{group_name}\" {{\n"
            for comp in group_components[:5]:  # Limit to first 5 components per group
                comp_name = comp['file_path'].replace('/', '_').replace('.', '_')
                plantuml_content += f"  [**{comp_name}**\\n{comp['language']}\\n{comp['lines_of_code']} LOC]\n"
            if len(group_components) > 5:
                plantuml_content += f"  note right: {len(group_components) - 5} more components...\n"
            plantuml_content += "}\n\n"
            
        plantuml_content += "@enduml"
        
        # Save and render diagram
        self._render_diagram(plantuml_content, 'component.png')
        
    def generate_data_flow_diagram(self, analysis_data: Dict[str, Any]):
        """Generate data flow diagram showing how data moves through the system"""
        components = analysis_data.get('components', [])
        
        plantuml_content = "@startuml\n"
        plantuml_content += "title Data Flow Diagram\n\n"
        plantuml_content += "skinparam rectangle {\n"
        plantuml_content += "  roundCorner 15\n"
        plantuml_content += "}\n\n"
        
        # Create external entities
        plantuml_content += "actor User\n"
        plantuml_content += "database Database\n\n"
        
        # Create main processing components (top 10 by complexity)
        sorted_components = sorted(components, key=lambda x: x.get('complexity', 0), reverse=True)
        main_components = sorted_components[:10]
        
        for i, comp in enumerate(main_components):
            comp_name = f"Component_{i+1}"
            plantuml_content += f"rectangle \"{comp_name}\\n{comp['language']}\" as C{i+1}\n"
            
        plantuml_content += "\n"
        
        # Add data flows
        plantuml_content += "User --> C1 : Request\n"
        for i in range(len(main_components) - 1):
            plantuml_content += f"C{i+1} --> C{i+2} : Processed Data\n"
        plantuml_content += f"C{len(main_components)} --> Database : Store Results\n"
        plantuml_content += f"Database --> C{len(main_components)} : Retrieve Data\n"
        plantuml_content += f"C1 --> User : Response\n"
        
        plantuml_content += "@enduml"
        
        self._render_diagram(plantuml_content, 'data-flow.png')
        
    def generate_sequence_diagram(self, analysis_data: Dict[str, Any]):
        """Generate sequence diagram showing typical execution flow"""
        components = analysis_data.get('components', [])
        
        plantuml_content = "@startuml\n"
        plantuml_content += "title Typical Execution Sequence\n\n"
        
        # Select key components for sequence
        key_components = []
        for comp in components:
            if 'main' in comp['file_path'].lower() or 'app' in comp['file_path'].lower():
                key_components.append(comp)
                
        if not key_components:
            # Fallback to top 5 most complex components
            sorted_components = sorted(components, key=lambda x: x.get('complexity', 0), reverse=True)
            key_components = sorted_components[:5]
            
        # Create participants
        plantuml_content += "actor User\n"
        for i, comp in enumerate(key_components):
            comp_name = f"Comp{i+1}"
            plantuml_content += f"participant \"{comp_name}\" as C{i+1}\n"
            
        plantuml_content += "\n"
        
        # Add sequence messages
        if key_components:
            plantuml_content += "User -> C1 : Initialize\n"
            for i in range(len(key_components) - 1):
                plantuml_content += f"C{i+1} -> C{i+2} : Process Request\n"
                plantuml_content += f"C{i+2} --> C{i+1} : Return Result\n"
            plantuml_content += "C1 -> User : Complete\n"
            
        plantuml_content += "@enduml"
        
        self._render_diagram(plantuml_content, 'sequence.png')
        
    def generate_architecture_topology(self, analysis_data: Dict[str, Any]):
        """Generate high-level architecture topology diagram"""
        repo_info = analysis_data.get('repo_info', {})
        
        plantuml_content = "@startuml\n"
        plantuml_content += "title System Architecture Topology\n\n"
        plantuml_content += "skinparam node {\n"
        plantuml_content += "  backgroundColor<<main>> LightBlue\n"
        plantuml_content += "  backgroundColor<<service>> LightGreen\n"
        plantuml_content += "  backgroundColor<<storage>> LightYellow\n"
        plantuml_content += "}\n\n"
        
        # Main application node
        plantuml_content += f"node \"{repo_info.get('name', 'Application')}\" <<main>> {{\n"
        
        # Add service layers
        plantuml_content += "  node \"API Layer\" <<service>>\n"
        plantuml_content += "  node \"Business Logic\" <<service>>\n"
        plantuml_content += "  node \"Data Access\" <<service>>\n"
        
        plantuml_content += "}\n\n"
        
        # External systems
        plantuml_content += "node \"External API\" <<service>>\n"
        plantuml_content += "database \"Database\" <<storage>>\n"
        plantuml_content += "cloud \"Message Queue\"\n\n"
        
        # Connections
        plantuml_content += "API Layer --> Business Logic\n"
        plantuml_content += "Business Logic --> Data Access\n"
        plantuml_content += "Business Logic --> External API\n"
        plantuml_content += "Data Access --> Database\n"
        plantuml_content += "Business Logic --> Message Queue\n"
        
        plantuml_content += "@enduml"
        
        self._render_diagram(plantuml_content, 'architecture.png')
        
    def _render_diagram(self, plantuml_content: str, filename: str):
        """Render PlantUML diagram to PNG"""
        diagram_path = os.path.join(self.diagrams_dir, filename.replace('.png', '.puml'))
        png_path = os.path.join(self.diagrams_dir, filename)
        
        # Save PlantUML file
        with open(diagram_path, 'w') as f:
            f.write(plantuml_content)
            
        # Render to PNG using plantuml command
        try:
            subprocess.run(['plantuml', '-tpng', diagram_path], check=True, capture_output=True)
            print(f"Generated diagram: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to render {filename} with PlantUML. Using placeholder.")
            # Create a simple placeholder image
            self._create_placeholder_image(png_path, filename)
        except FileNotFoundError:
            print(f"Warning: PlantUML not found. Creating placeholder for {filename}.")
            self._create_placeholder_image(png_path, filename)
            
    def _create_placeholder_image(self, png_path: str, title: str):
        """Create a simple placeholder image when PlantUML is not available"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fallback if not available
            try:
                font = ImageFont.load_default()
            except:
                font = None
                
            draw.rectangle([0, 0, 800, 600], outline='black', width=2)
            draw.text((50, 50), f"Architecture Diagram: {title}", fill='black', font=font)
            draw.text((50, 100), "Generated by Technical Insight Skill", fill='gray', font=font)
            draw.text((50, 150), "PlantUML not available - placeholder image", fill='red', font=font)
            
            img.save(png_path)
            print(f"Created placeholder: {png_path}")
        except ImportError:
            # If PIL is not available, create an empty file
            with open(png_path, 'w') as f:
                f.write("# Placeholder - PlantUML and PIL not available")
            print(f"Created text placeholder: {png_path}")
            
    def generate_all_diagrams(self, analysis_data_path: str):
        """Generate all architecture diagrams from analysis data"""
        print("Generating architecture diagrams...")
        
        # Load analysis data
        with open(analysis_data_path, 'r') as f:
            analysis_data = json.load(f)
            
        # Generate all diagram types
        self.generate_architecture_topology(analysis_data)
        self.generate_component_diagram(analysis_data)
        self.generate_data_flow_diagram(analysis_data)
        self.generate_sequence_diagram(analysis_data)
        
        print(f"All diagrams generated in {self.diagrams_dir}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python architecture-diagram-generator.py <analysis_data_path>")
        sys.exit(1)
        
    analysis_data_path = sys.argv[1]
    output_dir = os.path.dirname(os.path.dirname(analysis_data_path))
    
    generator = ArchitectureDiagramGenerator(output_dir)
    generator.generate_all_diagrams(analysis_data_path)