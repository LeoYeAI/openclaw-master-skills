#!/usr/bin/env python3
"""
Response Interpreter - Structures responses for AI agent analysis.

This module does NOT interpret responses itself. Instead, it:
1. Captures raw Nova Act responses
2. Structures them for the orchestrating AI agent (OpenClaw/Claude)
3. The AGENT does all the intelligent interpretation

The orchestrating agent should:
- Analyze if the goal was achieved based on the response
- Decide if retries are needed
- Generate alternative approaches
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import json


@dataclass
class StepResult:
    """Structured result for AI agent to analyze."""
    step_name: str
    prompt: str
    expected_outcome: str
    raw_response: str
    api_success: bool  # Did the API call work?
    error: Optional[str] = None
    attempts: int = 1
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def format_for_agent_analysis(results: List[Dict]) -> str:
    """
    Format test results for AI agent to analyze.
    
    The agent should look at each result and determine:
    1. Was the goal achieved? (based on raw_response content)
    2. Should we retry with a different approach?
    3. What's the overall test outcome?
    """
    output = []
    output.append("=" * 60)
    output.append("RESULTS FOR AI AGENT ANALYSIS")
    output.append("=" * 60)
    output.append("")
    output.append("For each step, analyze the raw_response to determine:")
    output.append("- goal_achieved: Did we find/accomplish what we were looking for?")
    output.append("- A 'No' or 'not found' response means goal NOT achieved")
    output.append("- Actual content/information means goal WAS achieved")
    output.append("")
    
    for i, result in enumerate(results, 1):
        output.append(f"--- Step {i}: {result.get('step_name', 'Unknown')} ---")
        output.append(f"Prompt: {result.get('prompt', 'N/A')}")
        output.append(f"Expected: {result.get('expected_outcome', 'N/A')}")
        output.append(f"API Success: {result.get('api_success', False)}")
        output.append(f"Raw Response: {result.get('raw_response', 'No response')}")
        if result.get('error'):
            output.append(f"Error: {result.get('error')}")
        output.append("")
    
    output.append("=" * 60)
    output.append("AGENT: Please analyze each step and provide:")
    output.append("1. goal_achieved (true/false) for each step")
    output.append("2. Overall test success/failure")
    output.append("3. Key findings and recommendations")
    output.append("=" * 60)
    
    return "\n".join(output)


def create_agent_prompt_for_interpretation(step_result: Dict) -> str:
    """
    Create a prompt that the orchestrating agent should use
    to interpret a single step result.
    """
    return f"""Analyze this usability test step result:

**Step:** {step_result.get('step_name', 'Unknown')}
**Question Asked:** {step_result.get('prompt', 'N/A')}
**Expected Outcome:** {step_result.get('expected_outcome', 'N/A')}
**Nova Act Response:** {step_result.get('raw_response', 'No response')}

Based on the response, determine:
1. **Goal Achieved?** Did we find/accomplish what we were looking for?
   - "No", "not found", "I don't see" = Goal NOT achieved
   - Actual content, "Yes", information found = Goal achieved
   
2. **Should Retry?** If goal not achieved, should we try a different approach?

3. **Next Action:** What should we do next?"""


def create_agent_prompt_for_alternative(
    original_prompt: str,
    failed_response: str,
    attempt_number: int
) -> str:
    """
    Create a prompt for the agent to generate an alternative approach.
    """
    return f"""The previous usability test step did not achieve its goal.

**Original Question:** {original_prompt}
**Response (goal not achieved):** {failed_response}
**Attempt:** {attempt_number} of 3

Please suggest an alternative approach to accomplish the same goal.
Consider:
- Looking in a different location (navigation vs content, header vs footer)
- Scrolling to see more of the page
- Rephrasing the question
- Broadening the search

Provide just the new question/prompt to try."""


# For backwards compatibility - but now just returns raw data
def interpret_response(prompt: str, response: str, expected_outcome: str = "") -> Dict:
    """
    Returns structured data for agent analysis.
    Does NOT interpret - that's the agent's job.
    """
    return {
        'prompt': prompt,
        'raw_response': str(response) if response else "",
        'expected_outcome': expected_outcome,
        'api_success': response is not None and response != "",
        'needs_agent_analysis': True
    }


def generate_alternative_approach(
    original_prompt: str,
    failed_response: str, 
    attempt_number: int
) -> Optional[str]:
    """
    Generate alternative browser commands when first attempt fails.
    
    NOTE: Keep prompts SIMPLE and DIRECT - no persona reasoning.
    Nova Act just executes browser actions; the agent interprets results.
    """
    if attempt_number > 3:
        return None
    
    prompt_lower = original_prompt.lower()
    
    # Extract the core task from the prompt (remove any persona language)
    # Common patterns to strip out
    core_prompt = original_prompt
    persona_prefixes = [
        r"as a \w+ with \w+ technical skills,?\s*",
        r"as a \w+,?\s*",
        r"for a \w+ user,?\s*",
        r"can you easily\s*",
    ]
    import re
    for pattern in persona_prefixes:
        core_prompt = re.sub(pattern, "", core_prompt, flags=re.IGNORECASE)
    core_prompt = core_prompt.strip()
    
    if attempt_number == 1:
        # Try looking in navigation
        if "navigation" in prompt_lower or "menu" in prompt_lower:
            return f"Look in the main content area instead: {core_prompt}"
        else:
            return f"Check the navigation menu for: {core_prompt}"
    
    if attempt_number == 2:
        # Try scrolling
        return f"Scroll down the page and look for: {core_prompt}"
    
    if attempt_number == 3:
        # Broaden search
        return f"List any elements on this page related to: {core_prompt}"
    
    return None
