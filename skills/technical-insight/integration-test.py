#!/usr/bin/env python3
"""
Integration test for the enhanced technical-insight skill
Tests the complete workflow from code analysis to diagram generation
"""

import os
import json
import tempfile
import shutil
from pathlib import Path

def test_complete_workflow():
    """Test the complete technical insight workflow"""
    print("🧪 Starting integration test...")
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = os.path.join(temp_dir, "test-tech")
        os.makedirs(output_dir)
        data_dir = os.path.join(output_dir, "data")
        diagrams_dir = os.path.join(output_dir, "diagrams")
        os.makedirs(data_dir)
        os.makedirs(diagrams_dir)
        
        # Create mock code analysis data
        mock_analysis_data = {
            'components': [
                {'file_path': 'main.go', 'lines_of_code': 150, 'imports': ['fmt', 'net/http'], 'complexity': 8, 'language': 'go'},
                {'file_path': 'pkg/handler/handler.go', 'lines_of_code': 200, 'imports': ['context', 'github.com/gorilla/mux'], 'complexity': 12, 'language': 'go'},
                {'file_path': 'pkg/database/db.go', 'lines_of_code': 180, 'imports': ['database/sql', 'github.com/lib/pq'], 'complexity': 10, 'language': 'go'}
            ],
            'dependencies': {
                'main.go': ['pkg/handler/handler.go'],
                'pkg/handler/handler.go': ['pkg/database/db.go']
            },
            'repo_info': {'url': 'https://github.com/test/repo', 'name': 'test-repo'}
        }
        
        # Save mock analysis data
        analysis_file = os.path.join(data_dir, 'code-analysis.json')
        with open(analysis_file, 'w') as f:
            json.dump(mock_analysis_data, f, indent=2)
            
        print(f"✅ Mock analysis data created: {analysis_file}")
        
        # Test diagram generation
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from architecture_diagram_generator import ArchitectureDiagramGenerator
        generator = ArchitectureDiagramGenerator(output_dir)
        generator.generate_all_diagrams(analysis_file)
        
        # Verify output files
        expected_diagrams = ['architecture.png', 'component.png', 'data-flow.png', 'sequence.png']
        generated_diagrams = []
        
        for diagram in expected_diagrams:
            diagram_path = os.path.join(diagrams_dir, diagram)
            if os.path.exists(diagram_path):
                generated_diagrams.append(diagram)
                print(f"✅ Generated: {diagram}")
            else:
                print(f"❌ Missing: {diagram}")
                
        # Test core mechanism template
        template_path = os.path.join(os.path.dirname(__file__), 'core-mechanism-template.md')
        if os.path.exists(template_path):
            print("✅ Core mechanism template exists")
        else:
            print("❌ Core mechanism template missing")
            
        # Test domain templates
        domain_templates = ['cloud-native.md']
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        for template in domain_templates:
            template_file = os.path.join(templates_dir, template)
            if os.path.exists(template_file):
                print(f"✅ Domain template exists: {template}")
            else:
                print(f"❌ Domain template missing: {template}")
                
        # Summary
        success = len(generated_diagrams) >= 3 and os.path.exists(template_path)
        if success:
            print("\n🎉 Integration test PASSED!")
            print(f"   Generated {len(generated_diagrams)}/4 diagrams")
            print("   All required templates present")
        else:
            print("\n💥 Integration test FAILED!")
            print(f"   Only {len(generated_diagrams)}/4 diagrams generated")
            
        return success

if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)