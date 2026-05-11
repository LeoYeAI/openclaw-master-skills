#!/usr/bin/env python3
"""
Adaptive AI-orchestrated usability testing - FULLY DYNAMIC VERSION.
Exploration strategy, prompts, and questions are all generated per test case.
"""

import sys
import os
import time
import json
import glob
import re
import signal
import atexit
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional

# Global state for graceful shutdown
_shutdown_state = {
    'all_results': [],
    'page_analysis': None,
    'test_start_time': None,
    'total_planned_tests': 0,
    'completed_tests': 0,
    'interrupted': False
}

def _generate_partial_report():
    """Generate report from whatever results we have on shutdown."""
    if _shutdown_state['interrupted']:
        return  # Already handled
    
    _shutdown_state['interrupted'] = True
    
    results = _shutdown_state['all_results']
    page_analysis = _shutdown_state['page_analysis']
    test_start_time = _shutdown_state['test_start_time']
    
    if not results or not page_analysis:
        print("\n⚠️ No results to save on shutdown")
        return
    
    print("\n" + "="*60)
    print("⚠️ INTERRUPTED - Generating partial report...")
    print("="*60)
    
    try:
        # Save whatever results we have
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Saved {len(results)} test results to {RESULTS_FILE}")
        
        # Get trace files from this run
        if test_start_time:
            trace_pattern = os.path.join(LOGS_DIR, "**", "*.html")
            all_traces = glob.glob(trace_pattern, recursive=True)
            traces = sorted(
                [t for t in all_traces if os.path.getmtime(t) >= test_start_time],
                key=os.path.getmtime
            )
        else:
            traces = []
        
        # Mark page analysis as partial
        page_analysis['_partial_report'] = True
        page_analysis['_completed_tests'] = _shutdown_state['completed_tests']
        page_analysis['_total_planned_tests'] = _shutdown_state['total_planned_tests']
        
        # Generate report
        from enhanced_report_generator import generate_enhanced_report
        report_path = generate_enhanced_report(page_analysis, results, traces)
        
        print(f"✅ Generated PARTIAL report: {report_path}")
        print(f"   ({_shutdown_state['completed_tests']}/{_shutdown_state['total_planned_tests']} tests completed)")
        
    except Exception as e:
        print(f"❌ Failed to generate partial report: {e}")

def _signal_handler(signum, frame):
    """Handle SIGTERM/SIGINT gracefully."""
    sig_name = signal.Signals(signum).name
    print(f"\n\n🛑 Received {sig_name} - shutting down gracefully...")
    _generate_partial_report()
    sys.exit(128 + signum)

# Register signal handlers
signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)

# Also generate report on normal exit if we have partial results
atexit.register(_generate_partial_report)

# Dynamic path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_DIR = os.getcwd()

sys.path.insert(0, SCRIPT_DIR)

from nova_session import nova_session
from enhanced_report_generator import generate_enhanced_report
from trace_finder import get_session_traces
from safe_nova_wrapper import safe_act_tuple as safe_act, safe_act_get_tuple as safe_act_get, safe_scroll, is_session_healthy, ActResult
from response_interpreter import interpret_response, generate_alternative_approach, format_for_agent_analysis
from dynamic_exploration import generate_exploration_strategy, adapt_prompt_for_persona
from status_reporter import start_status_reporter, stop_status_reporter, update_status, mark_complete, emit_final

WEBSITE_URL = "https://nova.amazon.com/act"  # Default
RESULTS_FILE = os.path.join(WORKSPACE_DIR, "test_results_adaptive.json")
LOGS_DIR = os.path.join(WORKSPACE_DIR, "nova_act_logs")

def load_cookbook() -> str:
    """Load the Nova Act cookbook for guidance on testing strategies and safety."""
    cookbook_path = os.path.join(SKILL_DIR, "references", "nova-act-cookbook.md")
    try:
        with open(cookbook_path, 'r') as f:
            content = f.read()
            print(f"✅ Loaded Nova Act cookbook ({len(content)} chars)")
            return content
    except Exception as e:
        print(f"⚠️ Could not load cookbook: {e}")
        return ""

class NavigationLinks(BaseModel):
    links: List[str]

class PageAnalysis(BaseModel):
    main_purpose: str
    key_features: List[str]
    target_audience: str

def analyze_page(url: str) -> Dict:
    """
    Step 1: Analyze the page with graceful error handling.
    """
    print(f"\n🔍 ANALYZING PAGE: {url}")
    print("="*60)
    
    analysis = {
        'title': 'Unknown',
        'navigation': [],
        'purpose': 'Unknown purpose',
        'visible_sections': ''
    }
    
    try:
        with nova_session(url, headless=True, logs_dir=LOGS_DIR) as nova:
            print("→ Reading page title and main heading...")
            ok, response, error = safe_act_get(
                nova,
                "What is the main title or headline on this page?",
                schema={"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]},
                timeout=20
            )
            if ok and response:
                analysis['title'] = response.get('title', 'Unknown')
                print(f"  Title: {analysis['title']}")
            else:
                print(f"  ⚠️ Could not extract title: {error}")
            
            if is_session_healthy(nova):
                print("→ Analyzing navigation...")
                ok, response, error = safe_act_get(
                    nova,
                    "List all the navigation links you see at the top of the page (just the text of each link, separated by commas)",
                    schema={"type": "object", "properties": {"links": {"type": "string"}}, "required": ["links"]},
                    timeout=20
                )
                if ok and response:
                    nav_text = response.get('links', '')
                    analysis['navigation'] = [link.strip() for link in nav_text.split(',') if link.strip()]
                    print(f"  Navigation: {analysis['navigation']}")
                else:
                    print(f"  ⚠️ Could not extract navigation: {error}")
            
            if is_session_healthy(nova):
                print("→ Understanding page purpose...")
                ok, response, error = safe_act_get(
                    nova,
                    "In one sentence, what does this page help users do?",
                    schema={"type": "object", "properties": {"purpose": {"type": "string"}}, "required": ["purpose"]},
                    timeout=20
                )
                if ok and response:
                    analysis['purpose'] = response.get('purpose', 'Unknown purpose')
                    print(f"  Purpose: {analysis['purpose']}")
                else:
                    print(f"  ⚠️ Could not extract purpose: {error}")
            
            # Get visible sections/areas on the page for agent analysis
            if is_session_healthy(nova):
                print("→ Identifying main content sections...")
                ok, response, error = safe_act_get(
                    nova,
                    "List the main sections or content areas visible on this page (e.g., 'hero banner, news feed, leaderboard sidebar, footer links'). Just describe what you see.",
                    schema={"type": "object", "properties": {"sections": {"type": "string"}}, "required": ["sections"]},
                    timeout=20
                )
                if ok and response:
                    analysis['visible_sections'] = response.get('sections', '')
                    print(f"  Sections: {analysis['visible_sections']}")
                else:
                    print(f"  ⚠️ Could not identify sections: {error}")
            
            # Note: The orchestrating AI agent will analyze this data
            # and determine what's important based on title, navigation, 
            # purpose, and visible sections. No need for hardcoded checks.
    
    except Exception as e:
        print(f"⚠️ Page analysis encountered error: {str(e)}")
        print("   Continuing with default analysis...")
    
    return analysis

def extract_json_safely(text: str) -> Optional[List]:
    """
    Safely extract JSON array from text (Bug #13: Better than regex).
    Tries multiple strategies:
    1. Direct parse (if response is pure JSON)
    2. Find array boundaries and parse
    3. Line-by-line cleanup
    """
    # Strategy 1: Try direct parse
    try:
        result = json.loads(text.strip())
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Find array boundaries
    start_idx = text.find('[')
    if start_idx == -1:
        return None
    
    # Find matching closing bracket
    depth = 0
    end_idx = -1
    for i, char in enumerate(text[start_idx:], start_idx):
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
            if depth == 0:
                end_idx = i
                break
    
    if end_idx == -1:
        return None
    
    try:
        result = json.loads(text[start_idx:end_idx + 1])
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Clean up common issues
    json_str = text[start_idx:end_idx + 1]
    # Remove trailing commas before ] or }
    cleaned = re.sub(r',\s*([}\]])', r'\1', json_str)
    try:
        result = json.loads(cleaned)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass
    
    return None


def infer_plausible_user_types(page_analysis: Dict) -> List[Dict]:
    """
    DEPRECATED (v1.4.0): Use AI agent-generated personas instead.
    
    This fallback uses Claude API to infer user types.
    Prefer passing AI-generated personas via the persona_arg parameter.
    
    Returns list of user type definitions with characteristics and goals.
    """
    print("→ [FALLBACK] Using AI to infer user types (prefer AI agent personas)...")
    
    purpose = page_analysis.get('purpose', 'Unknown')
    title = page_analysis.get('title', 'Unknown')
    navigation = ', '.join(page_analysis.get('navigation', []))
    
    prompt = f"""Based on this website analysis, identify the 3 most plausible user types who would visit this site in real life:

Website Title: {title}
Purpose: {purpose}
Navigation: {navigation}

For each of the 3 user types, provide:
1. archetype: A descriptive identifier (e.g., "frequent_business_traveler", "casual_sports_fan", "power_user")
2. name: A realistic first and last name for this persona
3. description: One sentence describing who they are (e.g., "Business professional who travels frequently for work")
4. age: Typical age (as a number)
5. tech_proficiency: Either "low", "medium", or "high"
6. goals: Array of exactly 3 specific goals this user would have on THIS website

Think about WHO actually uses this type of website. Be specific to this site's content and purpose.

Return EXACTLY 3 user types as a JSON array with this structure:
[
  {{"archetype": "...", "name": "...", "description": "...", "age": 35, "tech_proficiency": "medium", "goals": ["...", "...", "..."]}},
  ...
]"""
    
    try:
        import anthropic
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("  ⚠️ ANTHROPIC_API_KEY not set, using fallback personas")
            return []
        
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract JSON from response (Bug #13: Use safer extraction)
        content = response.content[0].text
        
        user_types = extract_json_safely(content)
        if user_types and len(user_types) >= 2:
            print(f"  ✅ AI identified {len(user_types)} plausible user types:")
            for ut in user_types:
                print(f"     • {ut.get('name', '?')} ({ut.get('archetype', '?')}): {ut.get('description', '?')}")
            return user_types[:3]  # Return top 3
        elif user_types:
            print(f"  ⚠️ AI returned only {len(user_types)} user types, need at least 2")
            return []
        else:
            print("  ⚠️ Could not parse JSON from AI response")
            return []
            
    except Exception as e:
        print(f"  ⚠️ AI inference failed: {e}")
        return []

def generate_personas_from_fallback_categories(page_analysis: Dict) -> tuple:
    """
    Fallback: Use hardcoded category detection when AI inference fails.
    Returns (personas_list, category_name).
    """
    purpose = page_analysis.get('purpose', '').lower()
    title = page_analysis.get('title', '').lower()
    navigation = ' '.join(page_analysis.get('navigation', [])).lower()
    
    personas = []
    site_category = None
    
    # Sports/Tournament sites
    if any(word in purpose + title + navigation for word in ['sport', 'tournament', 'game', 'score', 'player', 'team', 'league', 'match', 'golf', 'football', 'basketball', 'baseball']):
        site_category = 'sports'
        personas.append({
            "name": "Jordan Martinez",
            "archetype": "sports_enthusiast",
            "age": 34,
            "tech_proficiency": "medium",
            "goals": ["Find current standings/scores", "Check upcoming games/events", "View player/team statistics", "Access highlights or live coverage"],
            "description": "Sports fan who follows teams and tournaments regularly"
        })
        personas.append({
            "name": "Pat Wilson",
            "archetype": "casual_fan",
            "age": 52,
            "tech_proficiency": "low",
            "goals": ["Find basic information about favorite team", "Check game times", "Understand what's happening"],
            "description": "Casual sports viewer who checks in occasionally"
        })
    
    # E-commerce/Shopping sites
    elif any(word in purpose + title + navigation for word in ['shop', 'store', 'buy', 'product', 'cart', 'checkout', 'price', 'purchase', 'sale']):
        site_category = 'ecommerce'
        personas.append({
            "name": "Sam Taylor",
            "archetype": "online_shopper",
            "age": 29,
            "tech_proficiency": "high",
            "goals": ["Find specific products quickly", "Compare options and prices", "Read reviews", "Complete purchase efficiently"],
            "description": "Frequent online shopper who values efficiency and good deals"
        })
        personas.append({
            "name": "Maria Rodriguez",
            "archetype": "careful_buyer",
            "age": 45,
            "tech_proficiency": "medium",
            "goals": ["Research products thoroughly", "Ensure secure checkout", "Understand return policy", "Find customer service if needed"],
            "description": "Cautious shopper who researches before buying"
        })
    
    # News/Media sites
    elif any(word in purpose + title + navigation for word in ['news', 'article', 'story', 'blog', 'media', 'journalism', 'reporter']):
        site_category = 'news'
        personas.append({
            "name": "Alex Chen",
            "archetype": "news_reader",
            "age": 36,
            "tech_proficiency": "high",
            "goals": ["Find latest breaking news", "Read in-depth analysis", "Follow specific topics", "Share articles"],
            "description": "Regular news consumer who stays informed on current events"
        })
        personas.append({
            "name": "Dorothy Williams",
            "archetype": "occasional_reader",
            "age": 67,
            "tech_proficiency": "low",
            "goals": ["Find news on topics of interest", "Read without confusion", "Understand how to navigate"],
            "description": "Reads news occasionally, prefers simple, clear presentation"
        })
    
    # Booking/Travel sites
    elif any(word in purpose + title + navigation for word in ['book', 'reserve', 'hotel', 'flight', 'travel', 'vacation', 'rental', 'car rental']):
        site_category = 'booking'
        personas.append({
            "name": "Marcus Johnson",
            "archetype": "frequent_traveler",
            "age": 42,
            "tech_proficiency": "high",
            "goals": ["Book quickly and efficiently", "Find best rates", "Manage reservations", "Access loyalty benefits"],
            "description": "Business traveler who books frequently and values speed"
        })
        personas.append({
            "name": "Emma Davis",
            "archetype": "vacation_planner",
            "age": 38,
            "tech_proficiency": "medium",
            "goals": ["Research options thoroughly", "Compare prices and amenities", "Read reviews", "Understand cancellation policies"],
            "description": "Plans family vacations and wants to make informed decisions"
        })
    
    # Entertainment/Streaming sites
    elif any(word in purpose + title + navigation for word in ['watch', 'video', 'stream', 'show', 'movie', 'series', 'entertainment']):
        site_category = 'entertainment'
        personas.append({
            "name": "Taylor Kim",
            "archetype": "content_consumer",
            "age": 26,
            "tech_proficiency": "high",
            "goals": ["Find content to watch", "Browse recommendations", "Create watchlist", "Resume watching"],
            "description": "Regular viewer who enjoys discovering new content"
        })
        personas.append({
            "name": "Sarah Williams",
            "archetype": "casual_viewer",
            "age": 55,
            "tech_proficiency": "low",
            "goals": ["Find specific shows or movies", "Navigate without confusion", "Understand how to play content"],
            "description": "Watches occasionally, prefers simple interface"
        })
    
    # Developer/API/Technical sites
    elif any(word in purpose + title + navigation for word in ['developer', 'api', 'code', 'documentation', 'sdk', 'technical']):
        site_category = 'developer'
        personas.append({
            "name": "Alex Chen",
            "archetype": "developer",
            "age": 28,
            "tech_proficiency": "high",
            "goals": ["Integrate API", "Find technical docs", "See code examples", "Understand authentication"],
            "description": "Software developer looking to integrate this tool"
        })
        personas.append({
            "name": "Jordan Martinez",
            "archetype": "technical_lead",
            "age": 35,
            "tech_proficiency": "high",
            "goals": ["Evaluate technical capabilities", "Understand pricing/limits", "Assess security", "Check scalability"],
            "description": "Tech lead evaluating solutions for their team"
        })
    
    # SaaS/Business tools (default for unclear sites)
    else:
        site_category = 'saas'
        personas.append({
            "name": "Alex Chen",
            "archetype": "tech_savvy_user",
            "age": 28,
            "tech_proficiency": "high",
            "goals": ["Explore advanced features", "Try the tool", "Understand capabilities"],
            "description": "Tech-savvy early adopter"
        })
        personas.append({
            "name": "Marcus Johnson",
            "archetype": "business_professional",
            "age": 42,
            "tech_proficiency": "medium",
            "goals": ["Understand ROI", "Check pricing", "Evaluate ease of use"],
            "description": "Business professional evaluating tools"
        })
        if page_analysis.get('key_elements', {}).get('demo'):
            personas.append({
                "name": "Sarah Williams",
                "archetype": "beginner",
                "age": 35,
                "tech_proficiency": "low",
                "goals": ["Understand what it does", "Try simple example", "Get help if stuck"],
                "description": "First-time user with basic tech skills"
            })
    
    return personas, site_category

def generate_personas(page_analysis: Dict, user_persona_request: Optional[str] = None) -> List[Dict]:
    """
    Step 2: Generate contextual personas.
    
    Args:
        page_analysis: Analysis of the website
        user_persona_request: Optional user-specified persona description (e.g., "golf enthusiast tracking tournaments")
    
    Returns:
        List of persona dictionaries
    """
    print(f"\n👥 GENERATING PERSONAS")
    print("="*60)
    
    personas = []
    
    # If user specified a custom persona, create it
    if user_persona_request:
        print(f"→ Creating custom persona from user request: '{user_persona_request}'")
        
        # Parse the persona description to extract key attributes
        persona_desc_lower = user_persona_request.lower()
        
        # Determine tech proficiency based on description
        if any(word in persona_desc_lower for word in ['tech', 'developer', 'engineer', 'advanced', 'power']):
            tech_level = "high"
        elif any(word in persona_desc_lower for word in ['beginner', 'first-time', 'new', 'novice', 'elderly']):
            tech_level = "low"
        else:
            tech_level = "medium"
        
        # Determine archetype based on description
        if 'enthusiast' in persona_desc_lower or 'fan' in persona_desc_lower:
            archetype = "enthusiast"
            name = "Jordan Martinez"
        elif 'professional' in persona_desc_lower or 'business' in persona_desc_lower:
            archetype = "professional"
            name = "Alex Chen"
        elif 'casual' in persona_desc_lower or 'occasional' in persona_desc_lower:
            archetype = "casual_user"
            name = "Sam Williams"
        elif 'beginner' in persona_desc_lower or 'first-time' in persona_desc_lower:
            archetype = "beginner"
            name = "Sarah Johnson"
        else:
            archetype = "engaged_user"
            name = "Taylor Davis"
        
        # Extract goals based on context (website purpose + persona desc)
        purpose = page_analysis.get('purpose', '').lower()
        goals = []
        
        # Sport/content site goals
        if any(word in purpose for word in ['tournament', 'sport', 'score', 'game', 'match']):
            if 'following' in persona_desc_lower or 'tracking' in persona_desc_lower:
                goals = [
                    "Quickly find current tournament standings",
                    "Check latest scores and updates",
                    "View player/team statistics",
                    "Access live coverage or highlights"
                ]
        # E-commerce goals
        elif any(word in purpose for word in ['shop', 'buy', 'product', 'store']):
            if 'enthusiast' in persona_desc_lower:
                goals = [
                    "Find specific products in their interest area",
                    "Compare options and read reviews",
                    "Complete purchase quickly",
                    "Track orders and manage account"
                ]
        # Content/news goals
        elif any(word in purpose for word in ['news', 'article', 'content', 'blog']):
            goals = [
                "Find latest updates in area of interest",
                "Read in-depth articles",
                "Follow specific topics or tags",
                "Share content with others"
            ]
        # Default goals
        else:
            goals = [
                "Accomplish primary task efficiently",
                "Find relevant information easily",
                "Navigate without confusion"
            ]
        
        custom_persona = {
            "name": name,
            "archetype": archetype,
            "age": 32,  # Default reasonable age
            "tech_proficiency": tech_level,
            "goals": goals,
            "description": user_persona_request,
            "custom": True
        }
        
        personas.append(custom_persona)
        print(f"  ✅ Created: {name} ({archetype}, {tech_level} proficiency)")
        print(f"     Goals: {', '.join(goals[:2])}...")
        
        # Add one complementary persona for comparison
        if tech_level != "low":
            # Add a beginner persona for contrast
            personas.append({
                "name": "Pat Wilson",
                "archetype": "beginner",
                "age": 58,
                "tech_proficiency": "low",
                "goals": ["Understand the basics", "Navigate without getting lost", "Find help if needed"],
                "description": "First-time visitor with basic tech skills"
            })
            print(f"  ✅ Added contrast persona: Pat Wilson (beginner)")
    else:
        # No custom persona - use AI to infer plausible user types
        print(f"→ Auto-generating personas based on website exploration...")
        
        # Try AI-powered inference first
        ai_user_types = infer_plausible_user_types(page_analysis)
        
        if ai_user_types and len(ai_user_types) >= 2:
            # Success! Use AI-generated personas
            personas = ai_user_types
            print(f"  ✅ Using AI-generated personas")
        else:
            # Fallback to category-based detection
            print(f"  → Falling back to category-based persona generation...")
            personas, site_category = generate_personas_from_fallback_categories(page_analysis)
            print(f"  Detected site category: {site_category}")
        
        for p in personas:
            print(f"  → {p['name']} ({p['archetype']}): {p['description']}")
    
    return personas

def generate_test_cases(persona: Dict, page_analysis: Dict) -> List[str]:
    """Step 3: Generate realistic test cases (including workflow tests when appropriate)."""
    archetype = persona['archetype']
    key_elements = page_analysis.get('key_elements', {})
    has_pricing = key_elements.get('pricing', False)
    has_docs = key_elements.get('documentation', False)
    has_demo = key_elements.get('demo', False)
    purpose = page_analysis.get('purpose', '').lower()
    
    test_cases = []
    
    # Detect if this is a transactional/workflow-oriented site
    is_ecommerce = any(kw in purpose for kw in ['shop', 'store', 'buy', 'product', 'purchase'])
    is_booking = any(kw in purpose for kw in ['book', 'reserve', 'schedule', 'hotel', 'flight', 'appointment'])
    is_social = any(kw in purpose for kw in ['post', 'share', 'social', 'community', 'publish'])
    is_saas = any(kw in purpose for kw in ['signup', 'register', 'subscribe', 'trial'])
    
    # Generate workflow tests for transactional sites
    if is_ecommerce and archetype in ["tech_savvy_user", "business_professional"]:
        test_cases.append("Search for a product and add it to cart")
        test_cases.append("Complete checkout flow up to payment")
    elif is_booking:
        test_cases.append("Complete a booking workflow from search to checkout")
    elif is_social:
        test_cases.append("Create and prepare a post for publishing")
    elif is_saas:
        test_cases.append("Complete signup flow up to final submission")
    
    # Original information-finding tests
    if archetype == "developer" or archetype == "tech_savvy_user":
        if has_docs:
            test_cases.append("Find and access technical documentation")
        if has_demo:
            test_cases.append("Try the interactive demo or playground")
        if not is_ecommerce and not is_booking:  # Don't duplicate
            test_cases.append("Understand the core capabilities and features")
        
    elif archetype == "business_professional":
        if has_pricing:
            test_cases.append("Find pricing information and compare plans")
        test_cases.append("Evaluate if this meets business needs")
        
    elif archetype == "beginner":
        test_cases.append("Understand what this website does")
        if has_docs:
            test_cases.append("Find help or getting started guide")
    
    # If we still don't have test cases, use persona goals
    if not test_cases and 'goals' in persona:
        test_cases = [goal for goal in persona['goals'][:3]]
    
    # Fallback
    if not test_cases:
        test_cases = ["Explore the main features of the website"]
    
    return test_cases

def execute_exploration_step_adaptive(nova, step: Dict, persona: Dict, step_index: int = 0, max_attempts: int = 3) -> Dict:
    """
    Execute a single exploration step and capture RAW responses.
    
    IMPORTANT: This function does NOT interpret responses.
    The orchestrating AI agent (OpenClaw/Claude) should analyze the raw_response
    to determine if the goal was achieved.
    
    Returns structured data with:
    - raw_response: The actual text Nova Act returned
    - api_success: Whether the API call worked
    - needs_agent_analysis: Flag indicating agent should interpret
    """
    step_num = step_index
    action = step.get('prompt', step.get('action', ''))
    rationale = step.get('expected_outcome', step.get('rationale', ''))
    step_name = step.get('step_name', f'Step {step_num}')
    is_safety_stop = step.get('is_safety_stop', False)
    action_type = step.get('action_type', 'query')
    
    print(f"\n   Step {step_num}: {step_name}")
    print(f"   Action: {action[:80]}...")
    print(f"   Expected: {rationale}")
    if is_safety_stop:
        print(f"   ⚠️  SAFETY STOP: Will query only, no execution")
    
    result = {
        'step_number': step_num,
        'step_name': step_name,
        'prompt': action,
        'expected_outcome': rationale,
        'is_safety_stop': is_safety_stop,
        'raw_response': None,
        'api_success': False,
        'attempts': [],
        'error': None,
        'needs_agent_analysis': True  # Agent must interpret this!
    }
    
    # Adapt the action prompt for this persona
    adapted_action = adapt_prompt_for_persona(action, persona)
    current_prompt = adapted_action
    
    for attempt in range(1, max_attempts + 1):
        attempt_result = {
            'attempt': attempt,
            'prompt': current_prompt,
            'raw_response': None,
            'error': None
        }
        
        try:
            print(f"   → Attempt {attempt}/{max_attempts}: {current_prompt[:60]}...")
            
            if is_safety_stop:
                query_prompt = f"What would happen if I: {current_prompt}? Describe what you see but DO NOT execute the action."
                ok, response, error = safe_act_get(
                    nova, query_prompt,
                    schema={"type": "object", "properties": {"observation": {"type": "string"}}, "required": ["observation"]},
                    timeout=30
                )
                response_text = response.get('observation', '') if ok and response else None
                if not ok:
                    attempt_result['error'] = error
            
            elif action_type == 'navigate':
                ok, error_or_obs = safe_act(nova, current_prompt, timeout=30)
                if ok:
                    ok2, verification, _ = safe_act_get(
                        nova, "Briefly describe what you now see on the page",
                        schema={"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]},
                        timeout=20
                    )
                    response_text = verification.get('description', 'Navigation completed') if ok2 and verification else 'Navigation completed'
                else:
                    response_text = None
                    attempt_result['error'] = error_or_obs
            
            else:
                ok, response, error = safe_act_get(
                    nova, current_prompt,
                    schema={"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]},
                    timeout=30
                )
                response_text = response.get('answer', str(response)) if ok and response else None
                if not ok:
                    attempt_result['error'] = error
            
            attempt_result['raw_response'] = response_text
            
            if response_text:
                result['api_success'] = True
                result['raw_response'] = response_text
                print(f"   📝 Response: {response_text[:80]}...")
                print(f"   ⏳ (Agent will analyze if goal achieved)")
                result['attempts'].append(attempt_result)
                
                # Check for obvious negatives to try alternatives
                response_lower = response_text.lower().strip()
                obvious_negative = response_lower in ['no', 'false'] or \
                                   response_lower.startswith('no ') or \
                                   'not found' in response_lower or \
                                   'i don\'t see' in response_lower or \
                                   'i do not see' in response_lower
                
                if obvious_negative and attempt < max_attempts:
                    alt_prompt = generate_alternative_approach(adapted_action, response_text, attempt)
                    if alt_prompt:
                        print(f"   🔄 Response appears negative, trying alternative...")
                        current_prompt = alt_prompt
                        continue
                
                # Got a response - return it for agent analysis
                return result
            else:
                print(f"   ❌ No response: {attempt_result.get('error', 'Unknown error')}")
                result['error'] = attempt_result.get('error')
                
                if attempt < max_attempts:
                    alt_prompt = generate_alternative_approach(adapted_action, "No response", attempt)
                    if alt_prompt:
                        current_prompt = alt_prompt
                        print(f"   🔄 Retrying with different approach...")
        
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            attempt_result['error'] = str(e)
            result['error'] = str(e)
        
        result['attempts'].append(attempt_result)
    
    print(f"   ❌ All {max_attempts} attempts exhausted")
    return result


# Keep old function name for backwards compatibility
def execute_exploration_step(nova, step: Dict, persona: Dict, step_index: int = 0) -> Dict:
    """Wrapper for backwards compatibility."""
    return execute_exploration_step_adaptive(nova, step, persona, step_index, max_attempts=3)

def iterative_test_dynamic(persona: Dict, test_case: str, page_analysis: Dict, cookbook: str = "", website_url: str = None) -> Dict:
    """
    Execute one test case iteratively with dynamic strategy generation.
    """
    print(f"\n{'='*80}")
    print(f"🎭 TESTING: {persona['name']} ({persona['archetype']})")
    print(f"📋 TEST CASE: {test_case}")
    print(f"{'='*80}")
    
    result = {
        'persona': persona,
        'test_case': test_case,
        'steps': [],
        'overall_success': False,
        'completion_status': 'incomplete',
        'error': None,
        'trace_files': []
    }
    
    try:
        # Generate exploration strategy for this specific test case and persona
        steps = generate_exploration_strategy(test_case, persona, page_analysis, cookbook)
        
        if not steps:
            print("⚠️ Failed to generate exploration strategy")
            result['error'] = "Failed to generate exploration strategy"
            return result
        
        print(f"\n📝 Generated {len(steps)} exploration steps")
        
        # Capture existing trace files BEFORE this test
        trace_pattern = os.path.join(LOGS_DIR, "**", "*.html")
        existing_traces = set(glob.glob(trace_pattern, recursive=True))
        
        # Execute each step (Bug #11: use parameter instead of global)
        target_url = website_url or WEBSITE_URL
        with nova_session(target_url, headless=True, logs_dir=LOGS_DIR) as nova:
            for idx, step in enumerate(steps):
                step_result = execute_exploration_step(nova, step, persona, idx)
                result['steps'].append(step_result)
                
                # If a step fails completely (API error), stop
                if not step_result.get('api_success') and not step_result.get('is_safety_stop'):
                    print(f"\n⚠️ Step {idx} failed (API error), stopping test")
                    break
                
                # If goal not achieved after all retries, continue but note it
                if step_result.get('api_success') and not step_result.get('goal_achieved'):
                    print(f"   📝 Step {idx}: API worked but goal not achieved")
                
                # Small delay between steps
                time.sleep(0.5)
        
        # Capture NEW trace files created during this test
        all_traces = set(glob.glob(trace_pattern, recursive=True))
        new_traces = sorted(all_traces - existing_traces, key=os.path.getmtime)
        result['trace_files'] = new_traces
        if new_traces:
            print(f"\n🎬 Captured {len(new_traces)} trace file(s) for this test")
        
        # Count API successes - goal achievement will be determined by the orchestrating agent
        api_successes = sum(1 for s in result['steps'] if s.get('api_success', False))
        total_steps = len(result['steps'])
        
        # Raw data summary - agent will interpret and set actual success values
        result['api_successes'] = api_successes
        result['total_steps'] = total_steps
        result['needs_agent_analysis'] = True  # Agent MUST interpret raw_response values
        
        # Preliminary completion status based on API success only
        # Agent will update overall_success after interpreting responses
        if api_successes == total_steps:
            result['completion_status'] = 'complete'
        elif api_successes >= total_steps * 0.5:
            result['completion_status'] = 'partial'
        else:
            result['completion_status'] = 'incomplete'
        
        print(f"\n{'='*80}")
        print(f"📊 Raw data collected: {api_successes}/{total_steps} API calls succeeded")
        print(f"⏳ AWAITING AGENT ANALYSIS")
        print(f"   Agent must interpret raw_response in each step to determine goal achievement")
        print(f"{'='*80}")
    
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        result['error'] = str(e)
        result['completion_status'] = 'error'
    
    return result

def main():
    global WEBSITE_URL
    
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 run_adaptive_test.py <website_url> [persona_arg]")
        print("\nExamples:")
        print('  # Auto-generate personas (fallback)')
        print('  python3 run_adaptive_test.py "https://www.hertz.com/"')
        print()
        print('  # Custom persona description')
        print('  python3 run_adaptive_test.py "https://www.pgatour.com/" "golf enthusiast interested in the latest tournament"')
        print()
        print('  # AI-generated personas (JSON file)')
        print('  python3 run_adaptive_test.py "https://www.pgatour.com/" "personas.json"')
        print()
        print('  # AI-generated personas (JSON string)')
        print("  python3 run_adaptive_test.py \"https://www.pgatour.com/\" '[{\"name\":\"Jordan\",...}]'")
        sys.exit(1)
    
    WEBSITE_URL = sys.argv[1]
    persona_arg = sys.argv[2] if len(sys.argv) >= 3 else None
    
    # Determine what type of persona argument we received
    ai_generated_personas = None
    user_persona_request = None
    
    if persona_arg:
        # Check if it's a JSON file path
        if persona_arg.endswith('.json') and os.path.exists(persona_arg):
            print(f"\n🎯 Testing {WEBSITE_URL}")
            print(f"👥 Loading AI-generated personas from: {persona_arg}\n")
            try:
                with open(persona_arg, 'r') as f:
                    ai_generated_personas = json.load(f)
                    print(f"✅ Loaded {len(ai_generated_personas)} personas from file")
            except Exception as e:
                print(f"❌ Failed to load personas from {persona_arg}: {e}")
                print("   Falling back to auto-generation")
                ai_generated_personas = None
        
        # Check if it's a JSON string (starts with [ or {)
        elif persona_arg.strip().startswith(('[', '{')):
            print(f"\n🎯 Testing {WEBSITE_URL}")
            print(f"👥 Using AI-generated personas from argument\n")
            try:
                ai_generated_personas = json.loads(persona_arg)
                print(f"✅ Parsed {len(ai_generated_personas)} personas from JSON")
            except Exception as e:
                print(f"❌ Failed to parse JSON personas: {e}")
                print("   Treating as custom persona description instead")
                user_persona_request = persona_arg
        
        # Otherwise, treat as custom persona description
        else:
            print(f"\n🎯 Testing {WEBSITE_URL}")
            print(f"👤 Custom persona: {persona_arg}\n")
            user_persona_request = persona_arg
    else:
        print(f"\n🎯 Testing {WEBSITE_URL}")
        print(f"👤 Auto-generating personas (fallback mode)\n")
    
    # Start status reporter (60-second updates)
    reporter_process = start_status_reporter()
    
    # Record test start time for filtering trace files (Bug #10)
    test_start_time = time.time()
    _shutdown_state['test_start_time'] = test_start_time
    
    try:
        update_status("Loading cookbook...")
        cookbook = load_cookbook()
        
        update_status("Analyzing website...")
        page_analysis = analyze_page(WEBSITE_URL)
        _shutdown_state['page_analysis'] = page_analysis
        
        # Generate or use provided personas
        if ai_generated_personas:
            print(f"\n👥 USING AI-GENERATED PERSONAS")
            print("="*60)
            personas = ai_generated_personas
            for p in personas:
                print(f"  → {p.get('name', '?')} ({p.get('archetype', '?')}): {p.get('description', '?')}")
        else:
            update_status("Generating test personas...")
            personas = generate_personas(page_analysis, user_persona_request)
        
        if not personas:
            print("❌ Failed to generate personas")
            mark_complete(success=False)
            return
        
        # Calculate total planned tests for progress tracking
        total_planned = sum(len(generate_test_cases(p, page_analysis)) for p in personas)
        _shutdown_state['total_planned_tests'] = total_planned
        
        all_results = []
        _shutdown_state['all_results'] = all_results  # Share reference
        
        for i, persona in enumerate(personas, 1):
            update_status(f"Testing persona {i}/{len(personas)}: {persona['name']}...")
            
            test_cases = generate_test_cases(persona, page_analysis)
            print(f"\n📋 Generated {len(test_cases)} test cases for {persona['name']}")
            
            for j, test_case in enumerate(test_cases, 1):
                update_status(f"Running test {j}/{len(test_cases)} for {persona['name']}...")
                
                result = iterative_test_dynamic(persona, test_case, page_analysis, cookbook, website_url=WEBSITE_URL)
                all_results.append(result)
                _shutdown_state['completed_tests'] = len(all_results)
                
                # Save intermediate results
                with open(RESULTS_FILE, 'w') as f:
                    json.dump(all_results, f, indent=2)
        
        update_status("Generating final report...")
        
        # Generate HTML report with trace files from THIS test run only (Bug #10)
        trace_pattern = os.path.join(LOGS_DIR, "**", "*.html")
        all_traces = glob.glob(trace_pattern, recursive=True)
        # Filter to only traces created during this run
        traces = sorted(
            [t for t in all_traces if os.path.getmtime(t) >= test_start_time],
            key=os.path.getmtime
        )
        report_path = generate_enhanced_report(page_analysis, all_results, traces)
        
        print(f"\n{'='*80}")
        print(f"✅ ALL TESTS COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Report: {report_path}")
        print(f"📁 Results: {RESULTS_FILE}")
        print(f"🎬 Traces: {LOGS_DIR}")
        
        # Calculate success rate
        successful_tests = sum(1 for r in all_results if r['overall_success'])
        total_tests = len(all_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n✅ Complete: {successful_tests}/{total_tests} tests passed ({success_rate:.0f}%)")
        mark_complete(success=True)
        emit_final()
    
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        mark_complete(success=False)
    finally:
        stop_status_reporter()

if __name__ == "__main__":
    main()
