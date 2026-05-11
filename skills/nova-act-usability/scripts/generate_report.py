#!/usr/bin/env python3
"""
Generate HTML usability report from test results.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def analyze_results(results: List[Dict]) -> Dict:
    """
    Analyze test results and extract insights.
    
    Args:
        results: List of test result dicts
    
    Returns:
        Analysis dict with summary statistics and insights
    """
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get("success"))
    failed_tests = total_tests - successful_tests
    
    # Group by persona
    persona_stats = {}
    for result in results:
        persona = result.get("persona", "Unknown")
        if persona not in persona_stats:
            persona_stats[persona] = {"total": 0, "success": 0, "tasks": []}
        
        persona_stats[persona]["total"] += 1
        if result.get("success"):
            persona_stats[persona]["success"] += 1
        persona_stats[persona]["tasks"].append({
            "task": result.get("task"),
            "success": result.get("success"),
            "duration": result.get("duration_seconds"),
            "observations": result.get("observations", [])
        })
    
    # Find common friction points
    friction_points = []
    for result in results:
        for obs in result.get("observations", []):
            if not obs.get("success") or "friction" in obs.get("notes", "").lower():
                friction_points.append({
                    "persona": result.get("persona"),
                    "task": result.get("task"),
                    "issue": obs.get("notes")
                })
    
    return {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "failed_tests": failed_tests,
        "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
        "persona_stats": persona_stats,
        "friction_points": friction_points
    }


def generate_html_report(results: List[Dict], analysis: Dict, template_path: str, output_path: str):
    """
    Generate HTML report using template.
    
    Args:
        results: Raw test results
        analysis: Analyzed insights
        template_path: Path to HTML template
        output_path: Where to save report
    """
    # Load template
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Generate report sections
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    executive_summary = f"""
    <div class="executive-summary">
        <h2>Executive Summary</h2>
        <p><strong>Test Date:</strong> {timestamp}</p>
        <p><strong>Tests Conducted:</strong> {analysis['total_tests']}</p>
        <p><strong>Success Rate:</strong> {analysis['success_rate']:.1f}%</p>
        <p><strong>Personas Tested:</strong> {len(analysis['persona_stats'])}</p>
    </div>
    """
    
    # Per-persona findings
    persona_findings = "<h2>Persona Findings</h2>"
    for persona_name, stats in analysis['persona_stats'].items():
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        persona_findings += f"""
        <div class="persona-section">
            <h3>{persona_name}</h3>
            <p><strong>Tasks Completed:</strong> {stats['success']}/{stats['total']} ({success_rate:.1f}%)</p>
            <ul>
        """
        for task in stats['tasks']:
            status = "✓" if task['success'] else "✗"
            persona_findings += f"<li>{status} {task['task']} ({task['duration']:.1f}s)</li>"
        persona_findings += "</ul></div>"
    
    # Friction points
    friction_section = "<h2>Common Friction Points</h2><ul>"
    for fp in analysis['friction_points'][:10]:  # Top 10
        friction_section += f"<li><strong>{fp['persona']}</strong> - {fp['task']}: {fp['issue']}</li>"
    friction_section += "</ul>"
    
    # Recommendations
    recommendations = """
    <h2>Recommendations</h2>
    <ul>
        <li>Address high-friction areas identified in testing</li>
        <li>Improve accessibility for low tech proficiency users</li>
        <li>Optimize task completion paths</li>
        <li>Consider persona-specific UI adaptations</li>
    </ul>
    """
    
    # Replace template placeholders
    html = template.replace("{{EXECUTIVE_SUMMARY}}", executive_summary)
    html = html.replace("{{PERSONA_FINDINGS}}", persona_findings)
    html = html.replace("{{FRICTION_POINTS}}", friction_section)
    html = html.replace("{{RECOMMENDATIONS}}", recommendations)
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"Report generated: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_report.py <results_json_file> [output_html]")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "usability_report.html"
    
    # Load results
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Analyze
    analysis = analyze_results(results)
    
    # Find template
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "assets" / "report-template.html"
    
    # Generate report
    generate_html_report(results, analysis, str(template_path), output_file)


if __name__ == "__main__":
    main()
