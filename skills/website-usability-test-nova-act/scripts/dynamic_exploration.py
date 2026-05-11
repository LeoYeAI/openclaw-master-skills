#!/usr/bin/env python3
"""
Dynamic exploration strategy generator.
Uses cookbook guidance to generate contextual Nova Act prompts and workflows.
"""

from typing import Dict, List, Tuple
import json
import re

# Material impact keywords that require safety stops
MATERIAL_IMPACT_KEYWORDS = [
    # Monetary
    "buy", "purchase", "checkout", "pay", "subscribe", "donate", "order",
    # Communication
    "post", "publish", "share", "send", "email", "message", "tweet",
    # Account creation
    "sign up", "register", "create account", "join",
    # Submissions
    "submit", "apply", "enroll", "book", "reserve",
    # Newsletter/notifications
    "newsletter", "get updates", "notify"
]

def requires_safety_stop(test_case: str) -> bool:
    """Check if test case involves material impact and needs safety stop."""
    test_lower = test_case.lower()
    return any(keyword in test_lower for keyword in MATERIAL_IMPACT_KEYWORDS)

def detect_workflow_type(test_case: str) -> Tuple[bool, str]:
    """
    Determine if this is a workflow test (multi-step journey) vs information-finding.
    
    Returns: (is_workflow, workflow_type)
    """
    workflows = {
        "booking": ["book", "reserve", "schedule", "appointment"],
        "purchasing": ["buy", "purchase", "order", "checkout", "add to cart"],
        "posting": ["post", "publish", "share", "upload", "tweet", "comment"],
        "signup": ["sign up", "register", "create account", "join"],
        "submission": ["submit", "send", "contact", "apply", "enroll"],
        "search": ["search for", "find product", "look for item"]
    }
    
    test_lower = test_case.lower()
    for workflow_type, keywords in workflows.items():
        if any(kw in test_lower for kw in keywords):
            return True, workflow_type
    
    return False, "information_finding"

def parse_cookbook_hints(cookbook: str) -> Dict:
    """
    Extract actionable hints from cookbook content.
    Returns guidance for prompt construction.
    """
    hints = {
        "use_loose_matching": True,  # Default: avoid quotes for flexibility
        "small_steps": True,  # Break into small steps
        "observe_after_action": True,  # Check results after each action
        "use_schemas": True,  # Use structured extraction
        "max_steps": 30,  # Keep under 30 steps
    }
    
    if not cookbook:
        return hints
    
    cookbook_lower = cookbook.lower()
    
    # Check for matching guidance
    if "exact matching" in cookbook_lower and "quotes" in cookbook_lower:
        hints["matching_guidance"] = "Use quotes only for exact text; prefer loose matching for flexibility"
    
    # Check for step size guidance
    if "fewer than 30 steps" in cookbook_lower or "small steps" in cookbook_lower:
        hints["step_guidance"] = "Keep tasks small and atomic"
    
    # Check for observation guidance
    if "observe and analyze" in cookbook_lower:
        hints["observation_guidance"] = "Verify each action succeeded before proceeding"
    
    return hints


def generate_exploration_strategy(
    test_case: str,
    persona: Dict,
    page_analysis: Dict,
    cookbook: str = ""
) -> List[Dict]:
    """
    Generate a dynamic exploration strategy for a given test case.
    Uses cookbook guidance for workflow testing and safety stops.
    
    Args:
        test_case: What the user wants to accomplish
        persona: User persona with archetype and tech_proficiency
        page_analysis: Analysis of the target page
        cookbook: Nova Act cookbook content for prompt guidance (Bug #14: NOW USED!)
    
    Returns a list of exploration steps, each containing:
    - step_name: Human-readable step name
    - action_type: "query" or "navigate" or "scroll"
    - prompt: The actual Nova Act prompt to use
    - expected_outcome: What we're looking for
    - fallback_prompts: Alternative prompts if first fails
    - is_safety_stop: True if this step should observe but not execute
    
    This replaces hardcoded if/elif logic with contextual, cookbook-informed prompts.
    """
    
    # Parse cookbook for actionable guidance (Bug #14: Use the cookbook!)
    cookbook_hints = parse_cookbook_hints(cookbook)
    
    # Extract context
    archetype = persona.get('archetype', 'user')
    tech_level = persona.get('tech_proficiency', 'medium')
    page_title = page_analysis.get('title', 'this page')
    navigation = page_analysis.get('navigation', [])
    key_elements = page_analysis.get('key_elements', {})
    
    # Detect if this is a workflow test
    is_workflow, workflow_type = detect_workflow_type(test_case)
    needs_safety_stop = requires_safety_stop(test_case)
    
    if is_workflow:
        print(f"  🔄 Detected workflow type: {workflow_type}")
    if needs_safety_stop:
        print(f"  ⚠️  Safety stop required - will not complete final action")
    if cookbook:
        print(f"  📖 Using cookbook guidance for prompts")
    
    strategy = []
    
    # Apply cookbook guidance to prompts (Bug #14: Actually use cookbook!)
    def apply_cookbook_guidance(prompt: str) -> str:
        """Apply cookbook best practices to a prompt."""
        modified = prompt
        
        # Cookbook says: use loose matching (no quotes) for flexibility
        if cookbook_hints.get("use_loose_matching"):
            # Remove unnecessary quotes around search terms
            # e.g., 'link labeled "Documentation"' -> 'link with Documentation'
            modified = re.sub(r'"([^"]+)"', r'\1', modified)
        
        # Cookbook says: be direct and specific
        if cookbook_hints.get("step_guidance"):
            # Remove vague language
            modified = modified.replace("Let's see", "Check")
            modified = modified.replace("try to find", "find")
            modified = modified.replace("maybe look for", "look for")
        
        return modified
    
    # ===== WORKFLOW TESTS (Multi-step journeys) =====
    if is_workflow:
        if workflow_type == "booking":
            # Flight/hotel/appointment booking workflow
            strategy.extend([
                {
                    "step_name": "find_booking_form",
                    "action_type": "query",
                    "prompt": "Is there a search form or booking interface visible on this page?",
                    "expected_outcome": "Locate booking form",
                    "fallback_prompts": [
                        "Do you see input fields for dates, location, or search?",
                        "Is there a 'Book Now' or 'Search' button visible?"
                    ]
                },
                {
                    "step_name": "fill_search_criteria",
                    "action_type": "navigate",
                    "prompt": "Fill in the search form with test data: departure 'New York', destination 'Los Angeles', dates 2 weeks from now",
                    "expected_outcome": "Search form filled",
                    "fallback_prompts": []
                },
                {
                    "step_name": "initiate_search",
                    "action_type": "navigate",
                    "prompt": "Click the search or submit button to see results",
                    "expected_outcome": "Results displayed",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_results",
                    "action_type": "query",
                    "prompt": "Are booking options or results now displayed with relevant information?",
                    "expected_outcome": "Results visible",
                    "fallback_prompts": ["Did the page change to show available options?"]
                },
                {
                    "step_name": "select_option",
                    "action_type": "navigate",
                    "prompt": "Select the first available option",
                    "expected_outcome": "Option selected",
                    "fallback_prompts": []
                },
                {
                    "step_name": "proceed_to_details",
                    "action_type": "navigate",
                    "prompt": "Click continue, next, or proceed to enter details",
                    "expected_outcome": "Details form shown",
                    "fallback_prompts": []
                },
                {
                    "step_name": "fill_user_details",
                    "action_type": "navigate",
                    "prompt": "Fill in user details: Name 'Test User', Email 'test@example.com', Phone '5550123'",
                    "expected_outcome": "Details filled",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_checkout_accessible",
                    "action_type": "query",
                    "prompt": "Is there a 'Continue to Payment', 'Checkout', or 'Complete Booking' button visible?",
                    "expected_outcome": "⚠️ SAFETY STOP: Checkout accessible but NOT clicked",
                    "fallback_prompts": [],
                    "is_safety_stop": True
                }
            ])
            
        elif workflow_type == "purchasing":
            # E-commerce purchase workflow
            strategy.extend([
                {
                    "step_name": "search_product",
                    "action_type": "navigate",
                    "prompt": "Find and use the search function to search for 'laptop' or similar product",
                    "expected_outcome": "Product search executed",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_search_results",
                    "action_type": "query",
                    "prompt": "Are product search results displayed with images and prices?",
                    "expected_outcome": "Results shown",
                    "fallback_prompts": []
                },
                {
                    "step_name": "select_product",
                    "action_type": "navigate",
                    "prompt": "Click on the first product in the results",
                    "expected_outcome": "Product page loaded",
                    "fallback_prompts": []
                },
                {
                    "step_name": "add_to_cart",
                    "action_type": "navigate",
                    "prompt": "Click the 'Add to Cart' or 'Buy' button",
                    "expected_outcome": "Item added to cart",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_cart_updated",
                    "action_type": "query",
                    "prompt": "Is there confirmation the item was added (cart icon updated, notification shown, etc.)?",
                    "expected_outcome": "Cart confirmation",
                    "fallback_prompts": []
                },
                {
                    "step_name": "navigate_to_cart",
                    "action_type": "navigate",
                    "prompt": "Click on the cart icon or 'View Cart' button",
                    "expected_outcome": "Cart page loaded",
                    "fallback_prompts": []
                },
                {
                    "step_name": "proceed_to_checkout",
                    "action_type": "navigate",
                    "prompt": "Click 'Proceed to Checkout' or 'Checkout' button",
                    "expected_outcome": "Checkout initiated",
                    "fallback_prompts": []
                },
                {
                    "step_name": "fill_shipping",
                    "action_type": "navigate",
                    "prompt": "Fill shipping information: Name 'Test User', Address '123 Test St', City 'Test City', ZIP '12345'",
                    "expected_outcome": "Shipping filled",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_payment_page",
                    "action_type": "query",
                    "prompt": "Is there a payment method section, credit card form, or 'Complete Purchase' button visible?",
                    "expected_outcome": "⚠️ SAFETY STOP: Payment page accessible but NO PURCHASE MADE",
                    "fallback_prompts": [],
                    "is_safety_stop": True
                }
            ])
            
        elif workflow_type == "posting":
            # Social media posting workflow
            strategy.extend([
                {
                    "step_name": "find_create_button",
                    "action_type": "query",
                    "prompt": "Is there a 'Create Post', 'New Post', 'Tweet', or similar button visible?",
                    "expected_outcome": "Post creation button found",
                    "fallback_prompts": [
                        "Do you see a text box where you can write something?",
                        "Is there a '+' or 'Compose' button?"
                    ]
                },
                {
                    "step_name": "click_create",
                    "action_type": "navigate",
                    "prompt": "Click the post creation button or click in the text area",
                    "expected_outcome": "Compose interface opened",
                    "fallback_prompts": []
                },
                {
                    "step_name": "enter_content",
                    "action_type": "navigate",
                    "prompt": "Type test content: 'This is a usability test post - please ignore'",
                    "expected_outcome": "Content entered",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_post_button",
                    "action_type": "query",
                    "prompt": "Is there a 'Post', 'Publish', 'Share', or 'Tweet' button visible to complete posting?",
                    "expected_outcome": "⚠️ SAFETY STOP: Post button accessible but NOT clicked",
                    "fallback_prompts": [],
                    "is_safety_stop": True
                }
            ])
            
        elif workflow_type == "signup":
            # Account creation workflow
            strategy.extend([
                {
                    "step_name": "find_signup",
                    "action_type": "query",
                    "prompt": "Is there a 'Sign Up', 'Register', 'Create Account', or 'Join' button or link visible?",
                    "expected_outcome": "Signup button found",
                    "fallback_prompts": []
                },
                {
                    "step_name": "click_signup",
                    "action_type": "navigate",
                    "prompt": "Click the signup or register button",
                    "expected_outcome": "Registration form loaded",
                    "fallback_prompts": []
                },
                {
                    "step_name": "fill_registration",
                    "action_type": "navigate",
                    "prompt": "Fill registration form: Email 'test@example.com', Username 'testuser123', Password 'TestPass123!'",
                    "expected_outcome": "Form filled",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_submit_button",
                    "action_type": "query",
                    "prompt": "Is there a 'Create Account', 'Sign Up', or 'Register' button to submit the form?",
                    "expected_outcome": "⚠️ SAFETY STOP: Submit button accessible but NOT clicked",
                    "fallback_prompts": [],
                    "is_safety_stop": True
                }
            ])
            
        elif workflow_type == "submission":
            # Form submission workflow (contact, newsletter, etc.)
            strategy.extend([
                {
                    "step_name": "find_form",
                    "action_type": "query",
                    "prompt": "Is there a contact form, submission form, or input fields visible?",
                    "expected_outcome": "Form located",
                    "fallback_prompts": [
                        "Do you see a 'Contact Us' form?",
                        "Is there an email or message input field?"
                    ]
                },
                {
                    "step_name": "fill_form_fields",
                    "action_type": "navigate",
                    "prompt": "Fill the form with test data: Name 'Test User', Email 'test@example.com', Message 'Usability test message'",
                    "expected_outcome": "Fields filled",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_submit_accessible",
                    "action_type": "query",
                    "prompt": "Is there a 'Submit', 'Send', or 'Contact Us' button visible to complete submission?",
                    "expected_outcome": "⚠️ SAFETY STOP: Submit button accessible but NOT clicked",
                    "fallback_prompts": [],
                    "is_safety_stop": True
                }
            ])
            
        elif workflow_type == "search":
            # Product/content search workflow
            strategy.extend([
                {
                    "step_name": "find_search",
                    "action_type": "query",
                    "prompt": "Is there a search bar or search button visible?",
                    "expected_outcome": "Search function located",
                    "fallback_prompts": ["Do you see a magnifying glass icon or search input?"]
                },
                {
                    "step_name": "perform_search",
                    "action_type": "navigate",
                    "prompt": "Enter 'test query' into the search and press enter or click search",
                    "expected_outcome": "Search executed",
                    "fallback_prompts": []
                },
                {
                    "step_name": "verify_results",
                    "action_type": "query",
                    "prompt": "Are search results displayed that are relevant to the query?",
                    "expected_outcome": "Results shown",
                    "fallback_prompts": ["Did the page show any matching items or content?"]
                },
                {
                    "step_name": "assess_result_quality",
                    "action_type": "query",
                    "prompt": "Are the results clearly presented with relevant information (titles, descriptions, images)?",
                    "expected_outcome": "Results quality assessment",
                    "fallback_prompts": []
                }
            ])
        
        # Apply cookbook guidance to all prompts before returning
        for step in strategy:
            step['prompt'] = apply_cookbook_guidance(step['prompt'])
            step['fallback_prompts'] = [apply_cookbook_guidance(p) for p in step.get('fallback_prompts', [])]
        
        # Return workflow strategy early (don't mix with info-finding)
        return strategy
    
    # ===== INFORMATION-FINDING TESTS (Original logic) =====
    # Analyze the test case and generate appropriate exploration steps
    test_lower = test_case.lower()
    
    # ===== DOCUMENTATION / TECHNICAL RESOURCES =====
    if any(keyword in test_lower for keyword in ['documentation', 'docs', 'api', 'technical', 'developer']):
        # Step 1: Look in navigation first
        strategy.append({
            "step_name": "check_navigation_for_docs",
            "action_type": "query",
            "prompt": f"Is there a navigation link related to documentation, API, developer resources, or technical guides?",
            "expected_outcome": "Find docs link in nav",
            "fallback_prompts": [
                "Do you see any link with 'Docs', 'API', 'Developer', 'Guide', or 'Reference'?",
                "Is there a 'Resources' or 'Learn' section in the navigation?"
            ]
        })
        
        # Step 2: Check page content if nav fails
        strategy.append({
            "step_name": "check_page_for_docs",
            "action_type": "query",
            "prompt": f"Looking at the main content area, is there any mention of documentation, getting started guides, or technical resources?",
            "expected_outcome": "Find docs reference in content",
            "fallback_prompts": [
                "Are there any code snippets, API examples, or technical documentation visible?",
                f"Does {page_title} explain how developers can use or integrate this?"
            ]
        })
        
        # Tech-savvy users might look for specific things
        if tech_level == "high":
            strategy.append({
                "step_name": "check_advanced_docs",
                "action_type": "query",
                "prompt": "Are there links to GitHub, SDK downloads, or API reference documentation?",
                "expected_outcome": "Find advanced technical resources",
                "fallback_prompts": []
            })
    
    # ===== DEMO / INTERACTIVE FEATURES =====
    elif any(keyword in test_lower for keyword in ['demo', 'playground', 'try', 'interactive', 'example']):
        # Step 1: Look for interactive elements
        strategy.append({
            "step_name": "find_interactive_element",
            "action_type": "query",
            "prompt": "Is there an input field, text box, or interactive area where you can try something out?",
            "expected_outcome": "Find interactive element on page",
            "fallback_prompts": [
                "Do you see a 'Try it', 'Demo', or 'Playground' button or section?",
                "Is there anywhere you can type or interact with a live example?"
            ]
        })
        
        # Step 2: Check navigation
        strategy.append({
            "step_name": "check_nav_for_demo",
            "action_type": "query",
            "prompt": "Is there a navigation link for 'Demo', 'Playground', 'Try', or 'Examples'?",
            "expected_outcome": "Find demo link in navigation",
            "fallback_prompts": [
                "Do you see 'Get Started', 'Live Demo', or 'Interactive' in the menu?"
            ]
        })
        
        # Beginners need obvious calls-to-action
        if tech_level == "low":
            strategy.append({
                "step_name": "check_prominent_cta",
                "action_type": "query",
                "prompt": "Is there a large, obvious button near the top that invites you to try or start using the tool?",
                "expected_outcome": "Find beginner-friendly CTA",
                "fallback_prompts": []
            })
    
    # ===== PRICING / COST INFORMATION =====
    elif any(keyword in test_lower for keyword in ['pricing', 'price', 'cost', 'plan', 'subscription', 'fee']):
        # Step 1: Navigation check
        strategy.append({
            "step_name": "check_nav_for_pricing",
            "action_type": "query",
            "prompt": "Is there a 'Pricing', 'Plans', or 'Cost' link in the navigation menu?",
            "expected_outcome": "Find pricing in navigation",
            "fallback_prompts": [
                "Do you see 'Subscribe', 'Buy', or 'Get Started' with pricing info?",
                "Is there a 'Free' or 'Pro' tier mentioned in the navigation?"
            ]
        })
        
        # Step 2: Visible pricing on current page
        strategy.append({
            "step_name": "check_visible_pricing",
            "action_type": "query",
            "prompt": "Is there any pricing information, cost, or subscription tiers visible on the current page?",
            "expected_outcome": "Find pricing in content",
            "fallback_prompts": [
                "Do you see dollar amounts, price tags, or cost comparisons?",
                "Is there mention of 'free', 'premium', or different plan levels?"
            ]
        })
        
        # Step 3: Scroll for pricing
        strategy.append({
            "step_name": "scroll_for_pricing",
            "action_type": "scroll",
            "direction": "down",
            "prompt": "After scrolling, do you now see any pricing, cost, or subscription information?",
            "expected_outcome": "Find pricing after scroll",
            "fallback_prompts": []
        })
        
        # Business users care about transparency
        if archetype == "business_professional":
            strategy.append({
                "step_name": "check_transparent_pricing",
                "action_type": "query",
                "prompt": "If pricing is visible, are the actual dollar amounts clearly displayed, or is it 'contact us' / 'request quote'?",
                "expected_outcome": "Assess pricing transparency",
                "fallback_prompts": []
            })
    
    # ===== VALUE PROPOSITION / UNDERSTANDING =====
    elif any(keyword in test_lower for keyword in ['understand', 'value', 'what', 'purpose', 'does', 'benefit']):
        # Step 1: Check hero section
        strategy.append({
            "step_name": "check_hero_tagline",
            "action_type": "query",
            "prompt": "Near the top of the page, is there a clear headline or tagline that explains what this tool/product does or what problem it solves?",
            "expected_outcome": "Find clear value proposition",
            "fallback_prompts": [
                f"Does {page_title} have a sentence that tells you immediately what it's for?",
                "Is the main benefit or use case explained prominently?"
            ]
        })
        
        # Step 2: Supporting copy
        strategy.append({
            "step_name": "check_supporting_copy",
            "action_type": "query",
            "prompt": "Below the main headline, is there supporting text that elaborates on features, benefits, or how it works?",
            "expected_outcome": "Find detailed explanation",
            "fallback_prompts": [
                "Are there bullet points, feature lists, or use cases described?",
                "Can you quickly understand what makes this different or useful?"
            ]
        })
        
        # Beginners need simple language
        if tech_level == "low":
            strategy.append({
                "step_name": "check_simple_language",
                "action_type": "query",
                "prompt": "Is the description written in simple, non-technical language that anyone could understand?",
                "expected_outcome": "Assess language clarity",
                "fallback_prompts": [
                    "Are there lots of jargon, acronyms, or technical terms that might confuse a beginner?"
                ]
            })
    
    # ===== HELP / SUPPORT =====
    elif any(keyword in test_lower for keyword in ['help', 'support', 'contact', 'assistance', 'faq']):
        # Step 1: Header check
        strategy.append({
            "step_name": "check_header_for_help",
            "action_type": "query",
            "prompt": "In the top navigation or header area, is there a 'Help', 'Support', 'Contact', or 'FAQ' link?",
            "expected_outcome": "Find help in header",
            "fallback_prompts": [
                "Do you see 'Get Help', 'Contact Us', 'Support Center', or similar?",
                "Is there a question mark icon or help button visible?"
            ]
        })
        
        # Step 2: Footer check (scroll required)
        strategy.append({
            "step_name": "scroll_to_footer",
            "action_type": "scroll",
            "direction": "down",
            "prompt": "In the footer area, is there a 'Help', 'Support', 'Contact', or 'FAQ' link?",
            "expected_outcome": "Find help in footer",
            "fallback_prompts": [
                "Do you see contact email, phone number, or support links at the bottom?",
                "Is there a 'Help Center' or 'Resources' section in the footer?"
            ]
        })
        
        # Beginners might need more obvious help options
        if tech_level == "low":
            strategy.append({
                "step_name": "check_chat_widget",
                "action_type": "query",
                "prompt": "Is there a chat widget, chatbot, or live support button visible anywhere on the page?",
                "expected_outcome": "Find live help option",
                "fallback_prompts": []
            })
    
    # ===== GETTING STARTED / ONBOARDING =====
    elif any(keyword in test_lower for keyword in ['getting started', 'get started', 'onboard', 'begin', 'setup']):
        strategy.append({
            "step_name": "check_cta",
            "action_type": "query",
            "prompt": "Is there a prominent 'Get Started', 'Sign Up', 'Try Now', or 'Start Free' button or call-to-action?",
            "expected_outcome": "Find getting started CTA",
            "fallback_prompts": [
                "What's the main action button on this page?",
                "How would a new user begin using this product?"
            ]
        })
        
        strategy.append({
            "step_name": "check_onboarding_guide",
            "action_type": "query",
            "prompt": "Is there a 'Getting Started Guide', 'Quick Start', or step-by-step tutorial linked or visible?",
            "expected_outcome": "Find onboarding resources",
            "fallback_prompts": [
                "Are there numbered steps or a 'how to get started' section?",
                "Does the page explain the first steps clearly?"
            ]
        })
    
    # ===== GENERIC FALLBACK =====
    else:
        # If we don't recognize the test case, generate direct browser tasks
        # NOTE: Nova Act should NOT reason about personas - just execute browser actions
        # The agent interprets results in persona context afterward
        
        strategy.append({
            "step_name": "check_navigation",
            "action_type": "query",
            "prompt": f"List the main navigation menu items visible on this page",
            "expected_outcome": "Identify available navigation options",
            "fallback_prompts": [
                "What links are visible in the header or top navigation?",
                "What menu options can you see?"
            ]
        })
        
        strategy.append({
            "step_name": "find_relevant_link",
            "action_type": "query",
            "prompt": f"Is there a link or button related to: {test_case}?",
            "expected_outcome": "Find relevant element",
            "fallback_prompts": [
                f"What elements on this page might help with: {test_case}?",
                f"Do you see any text mentioning: {test_case}?"
            ]
        })
    
    # Apply cookbook guidance to all prompts before returning (Bug #14)
    for step in strategy:
        step['prompt'] = apply_cookbook_guidance(step['prompt'])
        step['fallback_prompts'] = [apply_cookbook_guidance(p) for p in step.get('fallback_prompts', [])]
    
    return strategy


def adapt_prompt_for_persona(base_prompt: str, persona: Dict) -> str:
    """
    NOTE: This function is intentionally minimal.
    
    Nova Act should NOT reason about personas - it just executes browser tasks.
    The Claude agent interprets results in the context of the persona afterward.
    
    We keep prompts simple and direct. The agent decides:
    - WHAT to test (based on persona goals)
    - HOW to interpret results (based on persona characteristics)
    
    Nova Act just:
    - Clicks, types, scrolls
    - Reports what it sees
    """
    # Return prompt unchanged - no persona-specific modifications
    # Persona context is used by the agent when interpreting results, not by Nova Act
    return base_prompt


def generate_fallback_questions(failed_step: Dict, context: Dict) -> List[str]:
    """
    If a step fails, generate contextual follow-up questions to try.
    
    This allows the test to adapt when the first approach doesn't work.
    """
    step_name = failed_step.get('step_name', '')
    
    fallbacks = []
    
    # If navigation check failed, try content area
    if 'navigation' in step_name or 'nav' in step_name:
        fallbacks.append("Ignoring the navigation menu, is the information visible anywhere in the main content area?")
        fallbacks.append("Is there a search box where you could search for this?")
    
    # If exact match failed, try fuzzy matching
    if 'exact' in step_name or 'specific' in step_name:
        fallbacks.append("Using different wording, is there anything similar or related visible?")
        fallbacks.append("What IS visible that might be related?")
    
    # If scroll didn't help, try other strategies
    if 'scroll' in step_name:
        fallbacks.append("Back at the top of the page, did we miss anything obvious?")
        fallbacks.append("Is there a sitemap, footer navigation, or breadcrumbs that might help?")
    
    return fallbacks
