#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from architecture_diagram_generator import ArchitectureDiagramGenerator

# Create test data directory
test_dir = "/tmp/test-diagrams"
os.makedirs(test_dir + "/data", exist_ok=True)
os.makedirs(test_dir + "/diagrams", exist_ok=True)

# Create mock analysis data
mock_data = {
    'components': [
        {'file_path': 'main.py', 'lines_of_code': 100, 'imports': ['os', 'sys'], 'complexity': 5, 'language': 'python'},
        {'file_path': 'utils/helper.py', 'lines_of_code': 80, 'imports': ['json', 'logging'], 'complexity': 3, 'language': 'python'}
    ],
    'dependencies': {},
    'repo_info': {'url': 'https://github.com/test/repo', 'name': 'test-repo'}
}

import json
with open(test_dir + "/data/code-analysis.json", "w") as f:
    json.dump(mock_data, f)

# Test diagram generation
generator = ArchitectureDiagramGenerator(test_dir)
generator.generate_all_diagrams(test_dir + "/data/code-analysis.json")

print("Test completed!")