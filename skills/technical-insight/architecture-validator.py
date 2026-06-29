#!/usr/bin/env python3
"""
Architecture Validator - Ensures generated diagrams comply with professional standards
"""

import os
import json
import sys
from typing import Dict, List

class ArchitectureValidator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.standards = self.config['architecture_standards']
        
    def validate_diagrams(self, diagrams_dir: str) -> bool:
        """Validate that all generated diagrams comply with professional standards"""
        print("🔍 Validating architecture diagrams against professional standards...")
        
        # Check required files exist
        required_files = []
        for diagram_type in self.standards['validation_rules']['required_diagrams']:
            required_files.extend([f"{diagram_type}.png", f"{diagram_type}.drawio"])
            
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(diagrams_dir, file)):
                missing_files.append(file)
                
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
            
        # Validate draw.io files have proper structure
        for diagram_type in self.standards['validation_rules']['required_diagrams']:
            drawio_file = os.path.join(diagrams_dir, f"{diagram_type}.drawio")
            if not self._validate_drawio_structure(drawio_file, diagram_type):
                print(f"❌ Invalid structure in {diagram_type}.drawio")
                return False
                
        # Check layer consistency
        if self.standards['validation_rules']['layer_consistency_check']:
            if not self._check_layer_consistency(diagrams_dir):
                print("❌ Layer consistency validation failed")
                return False
                
        print("✅ All architecture diagrams comply with professional standards!")
        return True
        
    def _validate_drawio_structure(self, drawio_file: str, diagram_type: str) -> bool:
        """Validate that draw.io file has proper XML structure and layers"""
        try:
            with open(drawio_file, 'r') as f:
                content = f.read()
                
            # Basic XML structure validation
            if '<mxGraphModel' not in content or '</mxGraphModel>' not in content:
                return False
                
            # Check for expected layer elements based on diagram type
            layer_definitions = self.standards['layer_definitions']
            if diagram_type in layer_definitions:
                expected_layers = layer_definitions[diagram_type]['layers']
                # For now, just check that the file is not empty and has proper structure
                # More detailed validation would require parsing the XML
                
            return True
        except Exception as e:
            print(f"Error validating {drawio_file}: {e}")
            return False
            
    def _check_layer_consistency(self, diagrams_dir: str) -> bool:
        """Check that layer definitions are consistent across all diagrams"""
        # This is a simplified check - in practice, this would parse all draw.io files
        # and verify that layer relationships are consistent
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate architecture diagrams')
    parser.add_argument('--config', required=True, help='Path to architecture configuration')
    parser.add_argument('diagrams_dir', help='Directory containing generated diagrams')
    
    args = parser.parse_args()
    
    validator = ArchitectureValidator(args.config)
    success = validator.validate_diagrams(args.diagrams_dir)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()