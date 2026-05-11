"""
AI Desktop Agent - Cognitive Desktop Automation
Combines vision, reasoning, and control for autonomous task execution
"""

import base64
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import logging

from desktop_control import DesktopController

logger = logging.getLogger(__name__)


class AIDesktopAgent:
    """
    Intelligent desktop agent that combines computer vision, LLM reasoning,
    and desktop control for autonomous task execution.
    
    Can understand screen content, plan actions, and execute complex workflows.
    """
    
    def __init__(self, llm_client=None, failsafe: bool = True):
        """
        Initialize AI Desktop Agent.
        
        Args:
            llm_client: OpenClaw LLM client for reasoning (optional, will try to auto-detect)
            failsafe: Enable failsafe mode
        """
        self.dc = DesktopController(failsafe=failsafe)
        self.llm_client = llm_client
        self.screen_width, self.screen_height = self.dc.get_screen_size()
        
        # Action history for learning
        self.action_history = []
        
        # Application knowledge base
        self.app_knowledge = self._load_app_knowledge()
        
        logger.info("AI Desktop Agent initialized")
    
    def _load_app_knowledge(self) -> Dict[str, Dict]:
        """
        Load application-specific knowledge.
        This can be extended with learned patterns.
        """
        return {
            "mspaint": {
                "name": "Microsoft Paint",
                "launch_command": "mspaint",
                "common_actions": {
                    "select_pencil": {"menu": "Tools", "position": "toolbar_left"},
                    "select_brush": {"menu": "Tools", "position": "toolbar"},
                    "select_color": {"menu": "Colors", "action": "click_palette"},
                    "draw_line": {"action": "drag", "tool_required": "line"},
                }
            },
            "notepad": {
                "name": "Notepad",
                "launch_command": "notepad",
                "common_actions": {
                    "type_text": {"action": "type"},
                    "save": {"hotkey": ["ctrl", "s"]},
                    "new_file": {"hotkey": ["ctrl", "n"]},
                }
            },
            "calculator": {
                "name": "Calculator",
                "launch_command": "calc",
                "common_actions": {
                    "calculate": {"action": "type_numbers"},
                }
            }
        }
    
    def execute_task(self, task: str, max_steps: int = 50) -> Dict[str, Any]:
        """
        Execute a high-level task autonomously.
        
        Args:
            task: Natural language task description
            max_steps: Maximum number of steps to attempt
            
        Returns:
            Execution result with status and details
        """
        logger.info(f"Executing task: {task}")
        
        # Initialize result
        result = {
            "task": task,
            "status": "in_progress",
            "steps": [],
            "screenshots": [],
            "success": False
        }
        
        try:
            # Step 1: Analyze task and plan
            plan = self._plan_task(task)
            logger.info(f"Generated plan with {len(plan)} steps")
            
            # Step 2: Execute plan step by step
            for step_num, step in enumerate(plan, 1):
                if step_num > max_steps:
                    logger.warning(f"Reached max steps ({max_steps})")
                    break
                
                logger.info(f"Step {step_num}/{len(plan)}: {step['description']}")
                
                # Capture screen before action
                screenshot_before = self.dc.screenshot()
                
                # Execute step
                step_result = self._execute_step(step)
                result["steps"].append(step_result)
                
                # Capture screen after action
                screenshot_after = self.dc.screenshot()
                result["screenshots"].append({
                    "step": step_num,
                    "before": screenshot_before,
                    "after": screenshot_after
                })
                
                # Verify step success
                if not step_result.get("success", False):
                    logger.error(f"Step {step_num} failed: {step_result.get('error')}")
                    result["status"] = "failed"
                    result["failed_at_step"] = step_num
                    return result
                
                # Small delay between steps
                time.sleep(0.5)
            
            result["status"] = "completed"
            result["success"] = True
            logger.info(f"Task completed successfully in {len(result['steps'])} steps")
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _plan_task(self, task: str) -> List[Dict[str, Any]]:
        """
        Plan task execution using LLM reasoning.
        
        Args:
            task: Task description
            
        Returns:
            List of execution steps
        """
        # For now, use rule-based planning
        # TODO: Integrate with OpenClaw LLM for intelligent planning
        
        # Parse task intent
        task_lower = task.lower()
        
        # Pattern matching for common tasks
        if "draw" in task_lower and "paint" in task_lower:
            return self._plan_paint_drawing(task)
        elif "type" in task_lower or "write" in task_lower:
            return self._plan_text_entry(task)
        elif "play" in task_lower and "game" in task_lower:
            return self._plan_game_play(task)
        elif "open" in task_lower or "launch" in task_lower:
            return self._plan_app_launch(task)
        else:
            # Generic plan - analyze and improvise
            return self._plan_generic(task)
    
    def _plan_paint_drawing(self, task: str) -> List[Dict]:
        """Plan for drawing in MS Paint."""
        # Extract what to draw
        drawing_subject = self._extract_subject(task)
        
        return [
            {
                "type": "launch_app",
                "app": "mspaint",
                "description": "Launch Microsoft Paint"
            },
            {
                "type": "wait",
                "duration": 2.0,
                "description": "Wait for Paint to load"
            },
            {
                "type": "activate_window",
                "title": "Paint",
                "description": "Ensure Paint window is active"
            },
            {
                "type": "select_tool",
                "tool": "pencil",
                "description": "Select pencil tool"
            },
            {
                "type": "draw",
                "subject": drawing_subject,
                "description": f"Draw {drawing_subject}"
            },
            {
                "type": "screenshot",
                "save_as": "drawing_result.png",
                "description": "Capture the drawing"
            }
        ]
    
    def _plan_text_entry(self, task: str) -> List[Dict]:
        """Plan for text entry task."""
        # Extract text to type
        text_content = self._extract_text_content(task)
        
        return [
            {
                "type": "launch_app",
                "app": "notepad",
                "description": "Launch Notepad"
            },
            {
                "type": "wait",
                "duration": 1.0,
                "description": "Wait for Notepad to load"
            },
            {
                "type": "type_text",
                "text": text_content,
                "wpm": 80,
                "description": f"Type: {text_content[:50]}..."
            }
        ]
    
    def _plan_game_play(self, task: str) -> List[Dict]:
        """Plan for playing a game."""
        game_name = self._extract_game_name(task)
        
        return [
            {
                "type": "analyze_screen",
                "description": "Analyze game screen"
            },
            {
                "type": "detect_game_state",
                "game": game_name,
                "description": f"Detect {game_name} state"
            },
            {
                "type": "execute_game_loop",
                "game": game_name,
                "max_iterations": 100,
                "description": f"Play {game_name}"
            }
        ]
    
    def _plan_app_launch(self, task: str) -> List[Dict]:
        """Plan for launching an application."""
        app_name = self._extract_app_name(task)
        
        return [
            {
                "type": "launch_app",
                "app": app_name,
                "description": f"Launch {app_name}"
            },
            {
                "type": "wait",
                "duration": 2.0,
                "description": f"Wait for {app_name} to load"
            }
        ]
    
    def _plan_generic(self, task: str) -> List[Dict]:
        """Generic planning fallback."""
        return [
            {
                "type": "analyze_screen",
                "description": "Analyze current screen state"
            },
            {
                "type": "infer_action",
                "task": task,
                "description": f"Infer action for: {task}"
            }
        ]
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step.
        
        Args:
            step: Step definition
            
        Returns:
            Execution result
        """
        step_type = step.get("type")
        result = {"step": step, "success": False}
        
        try:
            if step_type == "launch_app":
                self._do_launch_app(step["app"])
                result["success"] = True
                
            elif step_type == "wait":
                time.sleep(step["duration"])
                result["success"] = True
                
            elif step_type == "activate_window":
                success = self.dc.activate_window(step["title"])
                result["success"] = success
                
            elif step_type == "select_tool":
                self._do_select_tool(step["tool"])
                result["success"] = True
                
            elif step_type == "draw":
                self._do_draw(step["subject"])
                result["success"] = True
                
            elif step_type == "type_text":
                self.dc.type_text(step["text"], wpm=step.get("wpm", 80))
                result["success"] = True
                
            elif step_type == "screenshot":
                filename = step.get("save_as", "screenshot.png")
                self.dc.screenshot(filename=filename)
                result["success"] = True
                result["saved_to"] = filename
                
            elif step_type == "analyze_screen":
                analysis = self._analyze_screen()
                result["analysis"] = analysis
                result["success"] = True
                
            elif step_type == "execute_game_loop":
                game_result = self._execute_game_loop(step)
                result["game_result"] = game_result
                result["success"] = True
                
            else:
                result["error"] = f"Unknown step type: {step_type}"
                
        except Exception as e:
            logger.error(f"Step execution error: {e}")
            result["error"] = str(e)
        
        return result
    
    def _do_launch_app(self, app: str) -> None:
        """Launch an application."""
        # Get launch command from knowledge base
        app_info = self.app_knowledge.get(app, {})
        launch_cmd = app_info.get("launch_command", app)
        
        # Open Run dialog
        self.dc.hotkey('win', 'r')
        time.sleep(0.5)
        
        # Type and execute command
        self.dc.type_text(launch_cmd, wpm=100)
        self.dc.press('enter')
        
        logger.info(f"Launched: {app}")
    
    def _do_select_tool(self, tool: str) -> None:
        """Select a tool (e.g., in Paint)."""
        # This is simplified - in reality would use computer vision
        # to find and click the tool button
        
        # For Paint, tools are typically in the ribbon
        # We'll use hotkeys where possible
        if tool == "pencil":
            # In Paint, press 'P' for pencil
            self.dc.press('p')
        elif tool == "brush":
            self.dc.press('b')
        elif tool == "eraser":
            self.dc.press('e')
        
        logger.info(f"Selected tool: {tool}")
    
    def _do_draw(self, subject: str) -> None:
        """
        Draw something on screen.
        This is a simplified implementation - would be enhanced with:
        - Image generation (use wan2gp to generate reference)
        - Trace generation (convert image to draw commands)
        - Executed drawing (execute the commands)
        """
        logger.info(f"Drawing: {subject}")
        
        # Get canvas center (simplified - would detect canvas)
        canvas_x = self.screen_width // 2
        canvas_y = self.screen_height // 2
        
        # Simple drawing pattern (example: draw a    simple shape)
        if "circle" in subject.lower():
            self._draw_circle(canvas_x, canvas_y, radius=100)
        elif "square" in subject.lower():
            self._draw_square(canvas_x, canvas_y, size=200)
        elif "star" in subject.lower():
            self._draw_star(canvas_x, canvas_y, size=100)
        else:
            # Generic: draw a simple pattern
            self._draw_simple_pattern(canvas_x, canvas_y)
        
        logger.info(f"Completed drawing: {subject}")
    
    def _draw_circle(self, cx: int, cy: int, radius: int) -> None:
        """Draw a circle."""
        import math
        
        points = []
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x = int(cx + radius * math.cos(rad))
            y = int(cy + radius * math.sin(rad))
            points.append((x, y))
        
        # Draw by connecting points
        for i in range(len(points) - 1):
            self.dc.drag(points[i][0], points[i][1], 
                        points[i+1][0], points[i+1][1], 
                        duration=0.01)
        # Close the circle
        self.dc.drag(points[-1][0], points[-1][1], 
                    points[0][0], points[0][1], 
                    duration=0.01)
    
    def _draw_square(self, cx: int, cy: int, size: int) -> None:
        """Draw a square."""
        half = size // 2
        corners = [
            (cx - half, cy - half),  # Top-left
            (cx + half, cy - half),  # Top-right
            (cx + half, cy + half),  # Bottom-right
            (cx - half, cy + half),  # Bottom-left
        ]
        
        # Draw sides
        for i in range(4):
            start = corners[i]
            end = corners[(i + 1) % 4]
            self.dc.drag(start[0], start[1], end[0], end[1], duration=0.2)
    
    def _draw_star(self, cx: int, cy: int, size: int) -> None:
        """Draw a 5-pointed star."""
        import math
        
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            radius = size if i % 2 == 0 else size // 2
            x = int(cx + radius * math.cos(angle))
            y = int(cy + radius * math.sin(angle))
            points.append((x, y))
        
        # Draw by connecting points
        for i in range(len(points)):
            start = points[i]
            end = points[(i + 1) % len(points)]
            self.dc.drag(start[0], start[1], end[0], end[1], duration=0.1)
    
    def _draw_simple_pattern(self, cx: int, cy: int) -> None:
        """Draw a simple decorative pattern."""
        # Draw a few curved lines
        for offset in [-50, 0, 50]:
            self.dc.drag(cx - 100, cy + offset, 
                        cx + 100, cy + offset, 
                        duration=0.3)
    
    def _analyze_screen(self) -> Dict[str, Any]:
        """
        Analyze current screen state.
        Would use OCR, object detection in full implementation.
        """
        screenshot = self.dc.screenshot()
        active_window = self.dc.get_active_window()
        mouse_pos = self.dc.get_mouse_position()
        
        analysis = {
            "active_window": active_window,
            "mouse_position": mouse_pos,
            "screen_size": (self.screen_width, self.screen_height),
            "timestamp": time.time()
        }
        
        # TODO: Add OCR, object detection, UI element detection
        
        return analysis
    
    def _execute_game_loop(self, step: Dict) -> Dict:
        """
        Execute game playing loop.
        Would use reinforcement learning in full implementation.
        """
        game = step.get("game", "unknown")
        max_iter = step.get("max_iterations", 100)
        
        logger.info(f"Starting game loop for: {game}")
        
        result = {
            "game": game,
            "iterations": 0,
            "actions_taken": []
        }
        
        # Simple game loop - would be much more sophisticated
        for i in range(max_iter):
            # Analyze game state
            state = self._analyze_screen()
            
            # Decide action (simplified - would use ML model)
            action = self._decide_game_action(state, game)
            
            # Execute action
            self._execute_game_action(action)
            
            result["iterations"] += 1
            result["actions_taken"].append(action)
            
            # Check win/lose condition
            # (would detect from screen)
            
            time.sleep(0.1)
        
        return result
    
    def _decide_game_action(self, state: Dict, game: str) -> str:
        """Decide next game action based on state."""
        # Simplified - would use game-specific AI
        return "continue"
    
    def _execute_game_action(self, action: str) -> None:
        """Execute a game action."""
        # Simplified - would translate to specific inputs
        pass
    
    # Helper methods for parsing
    
    def _extract_subject(self, text: str) -> str:
        """Extract subject from drawing request."""
        # Simple extraction - would use NLP
        if "draw" in text.lower():
            parts = text.lower().split("draw")
            if len(parts) > 1:
                return parts[1].strip()
        return "unknown"
    
    def _extract_text_content(self, text: str) -> str:
        """Extract text content from typing request."""
        # Simple extraction
        if "type" in text.lower():
            parts = text.split("type")
            if len(parts) > 1:
                return parts[1].strip().strip('"').strip("'")
        return text
    
    def _extract_game_name(self, text: str) -> str:
        """Extract game name from request."""
        # Would use NER for better extraction
        return "unknown_game"
    
    def _extract_app_name(self, text: str) -> str:
        """Extract application name from request."""
        # Simple extraction - would use NER
        for app in self.app_knowledge.keys():
            if app in text.lower():
                return app
        return "notepad"  # Default fallback


# Quick access function
def create_agent(**kwargs) -> AIDesktopAgent:
    """Create an AI Desktop Agent instance."""
    return AIDesktopAgent(**kwargs)


if __name__ == "__main__":
    print("🤖 AI Desktop Agent - Cognitive Automation")
    print("=" * 60)
    
    # Create agent
    agent = AIDesktopAgent(failsafe=True)
    
    print("\n✨ Examples of what you can ask:")
    print("  - 'Draw a circle in Paint'")
    print("  - 'Type Hello World in Notepad'")
    print("  - 'Open Calculator'")
    print("  - 'Play Solitaire for me'")
    
    print("\n🎯 Try it:")
    task = input("\nWhat would you like me to do? ")
    
    if task.strip():
        result = agent.execute_task(task)
        print(f"\n{'='* 60}")
        print(f"Task Status: {result['status']}")
        print(f"Steps Executed: {len(result['steps'])}")
        print(f"Success: {result['success']}")
        
        if result.get('screenshots'):
            print(f"Screenshots captured: {len(result['screenshots'])}")
    else:
        print("\nNo task entered. Exiting.")
