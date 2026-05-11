#!/usr/bin/env python3
"""
Enhanced HTML report generator with detailed explanations and trace links.
"""

import os
from datetime import datetime
from typing import List, Dict

def is_wsl() -> bool:
    """Check if running on Windows Subsystem for Linux."""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
    except:
        return False

def convert_to_wsl_path(path: str) -> str:
    """Convert Linux path to WSL path accessible from Windows browser."""
    if is_wsl() and path.startswith('/'):
        # Convert /home/user/... to file://wsl$/Ubuntu/home/user/...
        return f"file://wsl$/Ubuntu{path}"
    elif path.startswith('/'):
        # Linux path to file:// URL
        return f"file://{path}"
    return path

def generate_enhanced_report(page_analysis: Dict, results: List[Dict], traces: List[str] = None) -> str:
    """
    Generate comprehensive HTML report with:
    - Links to Nova Act trace files (WSL-compatible)
    - Detailed explanations of each test
    - Easy dive-in points
    - Workflow testing support
    
    Args:
        page_analysis: Dict with website analysis (title, navigation, purpose, key_elements)
        results: List of test result dictionaries
        traces: Optional list of trace file paths from Nova Act sessions
    """
    traces = traces or []
    
    # Calculate summary stats
    total_tests = len(results)
    successful = sum(1 for r in results if r.get('overall_success', False))
    failed = total_tests - successful
    success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
    
    # Detect test type (workflow vs information-finding)
    test_types = set()
    for result in results:
        test_case = result.get('test_case', '').lower()
        if any(kw in test_case for kw in ['book', 'purchase', 'checkout', 'post', 'signup', 'submit']):
            test_types.add('workflow')
        else:
            test_types.add('information_finding')
    
    is_workflow_test = 'workflow' in test_types
    
    # Group by persona (using persona name as key since dict isn't hashable)
    persona_results = {}
    for result in results:
        persona = result['persona']
        persona_name = persona.get('name', 'Unknown')
        if persona_name not in persona_results:
            persona_results[persona_name] = {'persona': persona, 'results': []}
        persona_results[persona_name]['results'].append(result)
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Act Usability Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        
        h3 {{
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .page-analysis {{
            background: #e8f4f8;
            padding: 25px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }}
        
        .page-analysis h3 {{
            margin-top: 0;
            color: #2980b9;
        }}
        
        .page-analysis ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        .executive-summary {{
            background: #ecf0f1;
            padding: 25px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }}
        
        .executive-summary p {{
            margin: 10px 0;
            font-size: 1.1em;
        }}
        
        .executive-summary strong {{
            color: #2c3e50;
        }}
        
        .persona-section {{
            background: #fff;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 25px;
            margin: 25px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        }}
        
        .persona-section h3 {{
            color: #3498db;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .test-case {{
            background: #f8f9fa;
            border-left: 4px solid #95a5a6;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .test-case.success {{
            border-left-color: #2ecc71;
            background: #eafaf1;
        }}
        
        .test-case.failure {{
            border-left-color: #e74c3c;
            background: #fadbd8;
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .test-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .test-status {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .test-status.success {{
            background: #2ecc71;
            color: white;
        }}
        
        .test-status.failure {{
            background: #e74c3c;
            color: white;
        }}
        
        .test-status.pending {{
            background: #f39c12;
            color: white;
        }}
        
        .test-case.pending {{
            border-left-color: #f39c12;
            background: #fef9e7;
        }}
        
        .observation {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
        }}
        
        .observation-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .step-name {{
            font-weight: 600;
            color: #34495e;
        }}
        
        .step-result {{
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .step-result.success {{
            background: #d5f4e6;
            color: #27ae60;
        }}
        
        .step-result.failure {{
            background: #fadbd8;
            color: #c0392b;
        }}
        
        .observation-action {{
            color: #555;
            font-style: italic;
            margin: 5px 0;
        }}
        
        .observation-notes {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            margin-top: 8px;
            color: #555;
        }}
        
        .observation-notes.issue {{
            background: #fff3cd;
            border-left: 3px solid #ffc107;
        }}
        
        .trace-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 12px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .trace-link:hover {{
            background: #2980b9;
        }}
        
        .insights {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .insights h3 {{
            margin-top: 0;
            color: #f39c12;
        }}
        
        .insight-item {{
            margin: 10px 0;
            padding-left: 20px;
            position: relative;
        }}
        
        .insight-item:before {{
            content: "💡";
            position: absolute;
            left: 0;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .metric {{
            display: inline-block;
            margin: 0 15px;
            font-size: 1.1em;
        }}
        
        .metric-value {{
            font-weight: bold;
            color: #3498db;
            font-size: 1.3em;
        }}
        
        details {{
            margin: 15px 0;
        }}
        
        summary {{
            cursor: pointer;
            font-weight: 600;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            user-select: none;
        }}
        
        summary:hover {{
            background: #e9ecef;
        }}
        .partial-warning {{
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .partial-warning h2 {{
            color: #856404;
            margin: 0 0 10px 0;
            border: none;
            font-size: 1.5em;
        }}
        
        .partial-warning p {{
            color: #856404;
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🦅 Nova Act Usability Test Report</h1>
"""
    
    # Check if this is a partial report (interrupted)
    if page_analysis.get('_partial_report'):
        completed = page_analysis.get('_completed_tests', 0)
        total = page_analysis.get('_total_planned_tests', '?')
        html += f"""
        <div class="partial-warning">
            <h2>⚠️ PARTIAL REPORT - Test Interrupted</h2>
            <p>This report was generated after the test was interrupted (timeout or signal).</p>
            <p><strong>{completed} of {total} planned tests completed</strong></p>
            <p>Results below reflect only the tests that finished before interruption.</p>
        </div>
"""
    
    html += f"""
        <div class="page-analysis">
            <h3>📄 Page Analysis: {page_analysis.get('title', 'Unknown')}</h3>
            <p><strong>Purpose:</strong> {page_analysis.get('purpose', 'Not analyzed')}</p>
            <p><strong>Navigation:</strong> {', '.join(page_analysis.get('navigation', ['None found']))}</p>
"""
    
    # Dynamic key elements based on test type AND site category
    purpose_lower = page_analysis.get('purpose', '').lower()
    title_lower = page_analysis.get('title', '').lower()
    navigation = ' '.join(page_analysis.get('navigation', [])).lower()
    
    # Detect site category (same logic as persona generation)
    site_category = 'unknown'
    if any(word in purpose_lower + title_lower + navigation for word in ['sport', 'tournament', 'game', 'score', 'player', 'team', 'league', 'match']):
        site_category = 'sports'
    elif any(word in purpose_lower + title_lower + navigation for word in ['shop', 'store', 'buy', 'product', 'cart', 'checkout']):
        site_category = 'ecommerce'
    elif any(word in purpose_lower + title_lower + navigation for word in ['news', 'article', 'story', 'blog', 'media']):
        site_category = 'news'
    elif any(word in purpose_lower + title_lower + navigation for word in ['book', 'reserve', 'hotel', 'flight', 'travel', 'rental']):
        site_category = 'booking'
    elif any(word in purpose_lower + title_lower + navigation for word in ['watch', 'video', 'stream', 'show', 'movie']):
        site_category = 'entertainment'
    elif any(word in purpose_lower + title_lower + navigation for word in ['developer', 'api', 'code', 'documentation', 'sdk']):
        site_category = 'developer'
    else:
        site_category = 'saas'
    
    # Category-specific elements
    if site_category == 'sports':
        html += f"""
            <p><strong>Site Category:</strong> Sports/Tournament Content</p>
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Leaderboard/Standings: {'✅ Found in navigation' if 'leaderboard' in navigation or 'standing' in navigation else '⚠️ Not easily accessible'}</li>
                <li>Schedule/Calendar: {'✅ Found in navigation' if 'schedule' in navigation or 'calendar' in navigation else '⚠️ Not easily accessible'}</li>
                <li>Player/Team Stats: {'✅ Found in navigation' if 'player' in navigation or 'stats' in navigation or 'team' in navigation else '⚠️ Not easily accessible'}</li>
                <li>Live Scores/Updates: {'✅ Content suggests live coverage' if 'live' in purpose_lower or 'watch' in navigation else '⚠️ Not evident'}</li>
            </ul>
"""
    elif site_category == 'ecommerce':
        html += f"""
            <p><strong>Site Category:</strong> E-Commerce / Shopping</p>
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Product Search: {'✅ Available' if page_analysis.get('has_homepage_search') is True else '⚠️ Not immediately visible'}</li>
                <li>Shopping Cart: {'✅ Found in navigation' if 'cart' in navigation else '⚠️ Not easily accessible'}</li>
                <li>Checkout: {'✅ E-commerce functionality detected' if 'checkout' in navigation or 'cart' in navigation else '⚠️ Unclear'}</li>
                <li>Pricing: {'✅ Product pricing visible' if page_analysis.get('key_elements', {}).get('pricing') else '⚠️ Pricing not immediately clear'}</li>
            </ul>
"""
    elif site_category == 'news':
        html += f"""
            <p><strong>Site Category:</strong> News / Content / Media</p>
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Article Access: {'✅ Content-focused site' if 'news' in purpose_lower or 'article' in purpose_lower else '⚠️ Purpose unclear'}</li>
                <li>Navigation: {'✅ Clear menu structure' if len(page_analysis.get('navigation', [])) > 3 else '⚠️ Limited navigation'}</li>
                <li>Search: {'✅ Available' if page_analysis.get('has_homepage_search') is True else '⚠️ Not immediately visible'}</li>
                <li>Content Organization: {'✅ Categories/sections visible' if len(page_analysis.get('navigation', [])) > 5 else '⚠️ May be limited'}</li>
            </ul>
"""
    elif site_category == 'booking':
        html += f"""
            <p><strong>Site Category:</strong> Booking / Reservation / Travel</p>
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Search Widget: {'✅ Available' if page_analysis.get('has_homepage_search') is True else '❌ Not found - critical for booking sites'}</li>
                <li>Loyalty Program: {'✅ Visible' if page_analysis.get('has_loyalty_program') is True else '⚠️ Not prominently displayed'}</li>
                <li>Pricing Transparency: {'✅ Pricing info accessible' if page_analysis.get('key_elements', {}).get('pricing') else '⚠️ Pricing not upfront'}</li>
                <li>Booking Flow: {'✅ Clear path to reservation' if page_analysis.get('has_homepage_search') else '⚠️ May require exploration'}</li>
            </ul>
"""
    elif site_category == 'entertainment':
        html += f"""
            <p><strong>Site Category:</strong> Entertainment / Streaming / Video</p>
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Content Discovery: {'✅ Browse/categories available' if len(page_analysis.get('navigation', [])) > 3 else '⚠️ Limited browsing'}</li>
                <li>Search: {'✅ Available' if page_analysis.get('has_homepage_search') is True else '⚠️ Not immediately visible'}</li>
                <li>Watch/Play Access: {'✅ Video functionality detected' if 'watch' in navigation or 'video' in navigation else '⚠️ Unclear'}</li>
                <li>User Features: {'✅ Account/profile features' if 'sign' in navigation or 'account' in navigation else '⚠️ Not evident'}</li>
            </ul>
"""
    elif site_category == 'developer':
        html += f"""
            <p><strong>Site Category:</strong> Developer / API / Technical Documentation</p>
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Documentation: {'✅ Available' if page_analysis.get('key_elements', {}).get('documentation') else '❌ Not found - critical for developers'}</li>
                <li>API Reference: {'✅ Detected' if 'api' in navigation or 'reference' in navigation else '⚠️ Not easily accessible'}</li>
                <li>Code Examples: {'✅ Demo/playground available' if page_analysis.get('key_elements', {}).get('demo') else '⚠️ May be limited'}</li>
                <li>Getting Started: {'✅ Onboarding present' if 'start' in navigation or 'guide' in navigation else '⚠️ May require search'}</li>
            </ul>
"""
    else:  # saas or unknown
        html += f"""
            <p><strong>Site Category:</strong> SaaS / Business Tool</p>
            <p><strong>Key Features:</strong></p>
            <ul>
                <li>Documentation: {'✅ Available' if page_analysis.get('key_elements', {}).get('documentation') else '⚠️ Not found'}</li>
                <li>Interactive Demo: {'✅ Available' if page_analysis.get('key_elements', {}).get('demo') else '⚠️ Not found'}</li>
                <li>Pricing: {'✅ Available' if page_analysis.get('key_elements', {}).get('pricing') else '⚠️ Not found'}</li>
                <li>Getting Started: {'✅ Clear onboarding' if 'start' in navigation or 'docs' in navigation else '⚠️ May require exploration'}</li>
            </ul>
"""
    
    html += f"""
        </div>
        
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <p><strong>Test Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Tests Conducted:</strong> {total_tests}</p>
            <p>
                <span class="metric">
                    <span class="metric-value">{successful}</span> Passed
                </span>
                <span class="metric">
                    <span class="metric-value">{failed}</span> Failed
                </span>
                <span class="metric">
                    <span class="metric-value">{success_rate:.1f}%</span> Success Rate
                </span>
            </p>
            <p><strong>Personas Tested:</strong> {len(persona_results)}</p>
        </div>
"""
    
    # Per-persona detailed results
    html += "<h2>Detailed Test Results</h2>\n"
    
    # Global recording counter for consistent numbering across all tests
    global_recording_index = 1
    
    for persona_name, persona_data in persona_results.items():
        persona_tests = persona_data['results']
        persona_obj = persona_data['persona']
        
        persona_success = sum(1 for t in persona_tests if t.get('overall_success', False))
        persona_total = len(persona_tests)
        persona_rate = (persona_success / persona_total * 100) if persona_total > 0 else 0
        
        archetype = persona_obj.get('archetype', 'unknown')
        tech_level = persona_obj.get('tech_proficiency', 'medium')
        
        html += f"""
        <div class="persona-section">
            <h3>
                <span>{persona_name}</span>
                <span style="font-size: 0.8em; color: #7f8c8d;">({archetype} - {tech_level} proficiency)</span>
            </h3>
            <p><strong>Success Rate:</strong> {persona_success}/{persona_total} ({persona_rate:.1f}%)</p>
        """
        
        for test in persona_tests:
            steps = test.get('steps', [])
            overall_success = test.get('overall_success', False)
            has_error = test.get('error') or test.get('completion_status') == 'error'
            
            # Check if agent has interpreted this test
            test_interpreted = any('goal_achieved' in s for s in steps)
            
            # Determine display status
            if has_error and not steps:
                # Error before any steps ran - show as failed
                test_class = "failure"
                status_text = "❌ FAILED"
            elif test_interpreted or 'goals_achieved' in test:
                # Agent has interpreted - show actual result
                test_class = "success" if overall_success else "failure"
                status_text = "✅ PASSED" if overall_success else "❌ FAILED"
            elif test.get('needs_agent_analysis') and steps:
                # Has steps but not yet interpreted - show pending
                test_class = "pending"
                status_text = "⏳ PENDING"
            else:
                # Fallback
                test_class = "success" if overall_success else "failure"
                status_text = "✅ PASSED" if overall_success else "❌ FAILED"
            
            html += f"""
            <div class="test-case {test_class}">
                <div class="test-header">
                    <div class="test-title">{test['test_case']}</div>
                    <div class="test-status {test_class}">{status_text}</div>
                </div>
                <p><strong>Completion:</strong> {test.get('completion_status', 'unknown')}</p>
                
                <details open>
                    <summary>Step-by-Step Observations ({len(steps)} steps)</summary>
            """
            
            # Detailed observations
            for step in steps:
                step_num = step.get('step_number', 0)
                
                # Check if agent has interpreted this step
                # goal_achieved = agent's interpretation of whether the goal was met
                # If not set, agent analysis is still pending
                if 'goal_achieved' in step:
                    obs_success = step.get('goal_achieved', False)
                    needs_interpretation = False
                else:
                    # Fallback: show API status but mark as needing interpretation
                    obs_success = step.get('api_success', False)
                    needs_interpretation = step.get('needs_agent_analysis', True)
                
                if obs_success is True:
                    result_class = "success"
                    result_text = "✓"
                elif obs_success is False:
                    result_class = "failure"
                    result_text = "✗"
                else:
                    result_class = ""
                    result_text = "•"
                
                # Combine observations into notes - support both old and new formats
                observations_list = step.get('observations', [])
                raw_response = step.get('raw_response', '')
                error_msg = step.get('error', '')
                
                if observations_list:
                    notes = '; '.join(str(o) for o in observations_list)
                elif raw_response:
                    # Use raw_response as the observation
                    notes = f"Response: {raw_response}"
                elif error_msg:
                    notes = f"Error: {error_msg}"
                else:
                    notes = "No observations recorded"
                
                is_issue = any(word in notes.upper() for word in ['ERROR', 'FAILED', 'ISSUE', 'PROBLEM', 'CRITICAL'])
                notes_class = "issue" if is_issue else ""
                
                # Support both old format (action) and new format (prompt)
                action = step.get('action') or step.get('prompt', '') or 'No action'
                rationale = step.get('rationale') or step.get('expected_outcome', '')
                
                # Truncate action intelligently at word boundary
                if len(action) > 60:
                    action_display = action[:57].rsplit(' ', 1)[0] + '...'
                else:
                    action_display = action
                
                # Show warning if agent hasn't interpreted this step yet
                interpretation_warning = ""
                if needs_interpretation and 'goal_achieved' not in step:
                    interpretation_warning = '<div style="background: #fff3cd; padding: 5px 10px; border-radius: 3px; margin-top: 5px; font-size: 0.85em;">⏳ <strong>Awaiting agent interpretation</strong> - run analysis workflow to determine goal achievement</div>'
                
                html += f"""
                <div class="observation">
                    <div class="observation-header">
                        <span class="step-name">Step {step_num + 1}: {action_display}</span>
                        {f'<span class="step-result {result_class}">{result_text}</span>' if result_class else ''}
                    </div>
                    {f'<div style="color: #7f8c8d; font-size: 0.9em; margin: 5px 0;">Expected: {rationale}</div>' if rationale else ''}
                    <div class="observation-notes {notes_class}">
                        <strong>{"⚠️ " if is_issue else ""}Observation:</strong> {notes}
                    </div>
                    {interpretation_warning}
                </div>
                """
            
            html += """
                </details>
                
            """
            
            # Add Nova Act trace file links with global numbering
            trace_files = test.get('trace_files', [])
            if trace_files:
                # Calculate starting index for this test's recordings
                test_start_index = global_recording_index
                
                html += f"""
                <div style="margin-top: 15px; padding: 15px; background: #e3f2fd; border-radius: 4px;">
                    <strong>🔍 Nova Act Session Recordings ({len(trace_files)}):</strong>
                    <div style="margin-top: 10px;">
                """
                for trace_file in trace_files:
                    # Convert to WSL-compatible path if needed
                    browser_path = convert_to_wsl_path(trace_file)
                    display_name = os.path.basename(trace_file)
                    
                    html += f"""
                        <div style="margin: 5px 0;">
                            <a href="{browser_path}" class="trace-link" target="_blank">
                                📹 Recording {global_recording_index}: {display_name}
                            </a>
                            <span style="font-size: 0.85em; color: #666; margin-left: 10px;">
                                ({browser_path})
                            </span>
                        </div>
                    """
                    global_recording_index += 1
                    
                html += """
                    </div>
                    <p style="margin-top: 10px; font-size: 0.9em; color: #555;">
                        <em>Click to view detailed Nova Act trace showing every action, screenshot, and AI decision</em>
                    </p>
                </div>
                """
            
            html += "</div>\n"
        
        html += "</div>\n"
    
    # Key insights
    html += """
        <div class="insights">
            <h3>🔍 Key Insights</h3>
    """
    
    # Generate insights
    all_notes = []
    for test in results:
        for obs in test.get('observations', []):
            notes = obs.get('notes', '')
            if any(word in notes.upper() for word in ['ISSUE', 'FRICTION', 'CRITICAL', 'MAJOR', 'PROBLEM']):
                all_notes.append(notes)
    
    if all_notes:
        html += "<h4>UX Issues Discovered:</h4>\n"
        for note in set(all_notes):  # Unique issues
            html += f'<div class="insight-item">{note}</div>\n'
    
    # Success patterns
    successes = [t for t in results if t.get('overall_success', False)]
    if successes:
        html += "<h4>What Worked Well:</h4>\n"
        for test in successes[:3]:  # Top 3
            steps_count = len(test.get('steps', []))
            status = test.get('completion_status', 'unknown')
            html += f'<div class="insight-item">{test["test_case"]} - {status.title()} ({steps_count} steps)</div>\n'
    
    html += "</div>\n"
    
    # Session Recordings section (if traces provided)
    if traces:
        html += """
        <div class="insights" style="background: #e3f2fd; border-left-color: #2196f3;">
            <h3>🎬 Session Recordings</h3>
            <p style="margin-bottom: 15px;">Nova Act recorded detailed traces for each test session. Click to view step-by-step actions, screenshots, and AI decisions.</p>
        """
        for i, trace_file in enumerate(traces, 1):
            browser_path = convert_to_wsl_path(trace_file)
            display_name = os.path.basename(trace_file)
            # Extract session info from path if possible
            parent_dir = os.path.basename(os.path.dirname(trace_file))
            
            html += f"""
            <div style="margin: 8px 0; padding: 10px; background: white; border-radius: 4px;">
                <a href="{browser_path}" class="trace-link" target="_blank" style="text-decoration: none;">
                    📹 {display_name}
                </a>
                <div style="font-size: 0.85em; color: #666; margin-top: 5px;">
                    Session: {parent_dir}
                </div>
            </div>
            """
        html += "</div>\n"
    
    # Footer
    html += f"""
        <div class="footer">
            <p>Generated by Nova Act Usability Testing Suite | Powered by OpenClaw</p>
            <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write report to current working directory
    report_path = os.path.join(os.getcwd(), "nova_act_usability_report.html")
    with open(report_path, 'w') as f:
        f.write(html)
    
    return report_path
