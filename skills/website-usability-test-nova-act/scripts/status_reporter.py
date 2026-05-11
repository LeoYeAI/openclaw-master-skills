#!/usr/bin/env python3
"""
Status reporter for providing 60-second progress updates during long-running tests.
"""

import time
import threading
from typing import Optional, Callable
from datetime import datetime

class StatusReporter:
    """
    Reports test progress every 60 seconds in a background thread.
    """
    
    def __init__(self, update_interval: int = 60, output_func: Optional[Callable] = None):
        """
        Initialize status reporter.
        
        Args:
            update_interval: Seconds between status updates (default 60)
            output_func: Function to call with status messages (default: print)
        """
        self.update_interval = update_interval
        self.output = output_func or print
        self.running = False
        self.thread = None
        self.start_time = None
        
        # Status tracking
        self.current_phase = "Initializing"
        self.current_persona = None
        self.current_test = None
        self.tests_completed = 0
        self.tests_total = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start(self):
        """Start background status reporting."""
        if self.running:
            return
        
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._report_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop background status reporting."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def update_phase(self, phase: str):
        """Update current test phase."""
        self.current_phase = phase
    
    def update_persona(self, persona: str):
        """Update current persona being tested."""
        self.current_persona = persona
    
    def update_test(self, test_name: str, total: Optional[int] = None):
        """Update current test being executed."""
        self.current_test = test_name
        if total is not None:
            self.tests_total = total
    
    def mark_test_complete(self, success: bool):
        """Mark current test as complete."""
        self.tests_completed += 1
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        self.current_test = None
    
    def _report_loop(self):
        """Background loop that reports status every interval."""
        last_report = time.time()
        
        while self.running:
            time.sleep(1)  # Check every second
            
            if time.time() - last_report >= self.update_interval:
                self._emit_status()
                last_report = time.time()
    
    def _emit_status(self):
        """Emit current status report."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        
        # Build status message
        status_lines = [
            "",
            "="*60,
            f"📊 STATUS UPDATE ({datetime.now().strftime('%H:%M:%S')})",
            "="*60,
            f"⏱️  Elapsed Time: {elapsed_min}m {elapsed_sec}s",
            f"🔄 Current Phase: {self.current_phase}",
        ]
        
        if self.current_persona:
            status_lines.append(f"👤 Testing Persona: {self.current_persona}")
        
        if self.current_test:
            status_lines.append(f"🧪 Current Test: {self.current_test}")
        
        if self.tests_total > 0:
            progress_pct = (self.tests_completed / self.tests_total * 100)
            status_lines.append(f"📈 Progress: {self.tests_completed}/{self.tests_total} tests ({progress_pct:.0f}%)")
            status_lines.append(f"✅ Passed: {self.tests_passed}  |  ❌ Failed: {self.tests_failed}")
        
        status_lines.append("="*60)
        status_lines.append("")
        
        self.output("\n".join(status_lines))
    
    def emit_final_report(self):
        """Emit final status when test completes."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        
        success_rate = (self.tests_passed / self.tests_total * 100) if self.tests_total > 0 else 0
        
        report_lines = [
            "",
            "="*60,
            "🎉 TEST COMPLETE",
            "="*60,
            f"⏱️  Total Time: {elapsed_min}m {elapsed_sec}s",
            f"📊 Tests Run: {self.tests_completed}/{self.tests_total}",
            f"✅ Passed: {self.tests_passed}",
            f"❌ Failed: {self.tests_failed}",
            f"📈 Success Rate: {success_rate:.1f}%",
            "="*60,
            ""
        ]
        
        self.output("\n".join(report_lines))


# Convenience functions for easy integration
_global_reporter: Optional[StatusReporter] = None

def start_status_reporter(update_interval: int = 60):
    """Start global status reporter (call at test start)."""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = StatusReporter(update_interval=update_interval)
    _global_reporter.start()
    return _global_reporter

def stop_status_reporter():
    """Stop global status reporter (call at test end)."""
    global _global_reporter
    if _global_reporter:
        _global_reporter.stop()

def get_reporter() -> Optional[StatusReporter]:
    """Get the global status reporter instance."""
    return _global_reporter

def update_status(phase: Optional[str] = None, 
                  persona: Optional[str] = None, 
                  test: Optional[str] = None,
                  total: Optional[int] = None):
    """Update current test status (convenience function)."""
    reporter = get_reporter()
    if reporter:
        if phase:
            reporter.update_phase(phase)
        if persona:
            reporter.update_persona(persona)
        if test:
            reporter.update_test(test, total)

def mark_complete(success: bool):
    """Mark current test as complete (convenience function)."""
    reporter = get_reporter()
    if reporter:
        reporter.mark_test_complete(success)

def emit_final():
    """Emit final status report (convenience function)."""
    reporter = get_reporter()
    if reporter:
        reporter.emit_final_report()
