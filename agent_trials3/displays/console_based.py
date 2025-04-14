import sys
import threading
import queue
import time
from typing import List, Dict, Any, Tuple, Optional
import os

class AgentDisplay:
    """
    A console-only version of AgentDisplay that works reliably on Ubuntu systems
    where PyGame encounters OpenGL issues. This class provides the same API as the
    original AgentDisplay but outputs everything to the console instead of a GUI.
    """
    
    def __init__(self, width=1200, height=800):
        # We ignore width/height since we're console-only
        print("Initializing Console-Only Agent Display")
        
        # State data
        self.input_text = ""
        self.steps_executed = []
        self.steps_planned = []
        self.thinking_lines = []
        self.function_calls = []
        self.errors = []
        
        # UI thread control
        self.running = False
        self.ui_thread = None
        self.ui_queue = queue.Queue()
        
        # Terminal formatting (if supported)
        self.use_colors = True
        try:
            # Check if terminal supports colors
            if os.name == 'nt':  # Windows
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                self.use_colors = True
            else:  # Unix/Linux
                self.use_colors = 'TERM' in os.environ and os.environ['TERM'] != 'dumb'
        except:
            self.use_colors = False
        
        # Color codes for console output
        if self.use_colors:
            self.BLUE = '\033[94m'
            self.GREEN = '\033[92m'
            self.YELLOW = '\033[93m'
            self.PURPLE = '\033[95m'
            self.RED = '\033[91m'
            self.BOLD = '\033[1m'
            self.END = '\033[0m'
        else:
            self.BLUE = self.GREEN = self.YELLOW = self.PURPLE = self.RED = self.BOLD = self.END = ''
        
    def start(self):
        """Start the UI thread"""
        if not self.running:
            self.running = True
            # Start a console output thread
            self.ui_thread = threading.Thread(target=self._console_loop)
            self.ui_thread.daemon = True
            self.ui_thread.start()
            
            # Print header
            print("\n" + self.BOLD + "=" * 80 + self.END)
            print(self.BOLD + "AGENT FRAMEWORK UI (CONSOLE MODE)" + self.END)
            print(self.BOLD + "=" * 80 + self.END + "\n")
            
    def stop(self):
        """Stop the UI thread"""
        self.running = False
        if self.ui_thread:
            self.ui_thread.join(timeout=1.0)
    
    def _console_loop(self):
        """Console output loop for processing messages"""
        while self.running:
            try:
                # Process UI queue
                if not self.ui_queue.empty():
                    cmd, args = self.ui_queue.get_nowait()
                    
                    if cmd == 'input':
                        self._print_section("INPUT", self.BLUE, args)
                    elif cmd == 'steps':
                        executed, planned = args
                        self._print_section("STEPS", self.GREEN, None)
                        print(f"{self.GREEN}Executed:{self.END}")
                        for i, (step, result) in enumerate(executed):
                            print(f"{self.GREEN}{i+1}. {step}{self.END}")
                            print(f"{self.GREEN}   Result: {result}{self.END}")
                        print(f"\n{self.GREEN}Planned:{self.END}")
                        for i, step in enumerate(planned):
                            print(f"{self.GREEN}{i+1}. {step}{self.END}")
                    elif cmd == 'thinking':
                        self._print_section("THINKING", self.YELLOW, args)
                    elif cmd == 'function':
                        name, params, result = args
                        self._print_section("FUNCTION CALL", self.PURPLE, None)
                        print(f"{self.PURPLE}Function: {name}{self.END}")
                        print(f"{self.PURPLE}Parameters:{self.END}")
                        for k, v in params.items():
                            print(f"{self.PURPLE}  {k}: {v}{self.END}")
                        print(f"{self.PURPLE}Result: {result}{self.END}")
                    elif cmd == 'error':
                        self._print_section("ERROR", self.RED, args)
                    
                    self.ui_queue.task_done()
                    
                # Sleep to avoid CPU hogging
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in console output loop: {e}")
                time.sleep(1)  # Longer sleep on error
    
    def _print_section(self, title, color, content):
        """Print a formatted section to the console"""
        print(f"\n{color}{self.BOLD}===== {title} ====={self.END}")
        if content:
            print(f"{color}{content}{self.END}")
    
    # Public interface methods for the agent to call
    
    def input(self, text):
        """Update the input display"""
        self.input_text = text
        self.ui_queue.put(('input', text))
    
    def update_steps(self, executed, planned):
        """Update the steps display"""
        self.steps_executed = executed
        self.steps_planned = planned
        self.ui_queue.put(('steps', (executed, planned)))
    
    def thinking(self, text):
        """Add a line to the thinking process display"""
        self.thinking_lines.append(text)
        self.ui_queue.put(('thinking', text))
    
    def function(self, name, params, result):
        """Add a function call to the function calls display"""
        formatted_call = {
            'name': name,
            'params': params,
            'result': result
        }
        self.function_calls.append(formatted_call)
        self.ui_queue.put(('function', (name, params, result)))
    
    def error(self, text):
        """Add an error to the errors display"""
        self.errors.append(text)
        self.ui_queue.put(('error', text))


# To use this file, you would need to:
# 1. Save it as agent_trials3/display.py in your project
# 2. No other changes needed - this is a drop-in replacement

# If you want to test it directly:
if __name__ == "__main__":
    display = AgentDisplay()
    
    # Start the display
    display.start()
    
    # Add some example data
    display.input("Example user query about data analysis")
    display.thinking("Analyzing the user's question...")
    display.thinking("Determining appropriate analysis steps...")
    display.update_steps(
        [("Parse user query", "Identified request for data visualization")], 
        ["Retrieve data", "Clean data", "Create visualization"]
    )
    display.function("retrieve_data", {"source": "database"}, "Retrieved 1000 records")
    display.error("This is an example error message")
    
    # In a real application, this would be controlled by the agent
    try:
        # Keep running for a while to see the output
        for i in range(5):
            time.sleep(1)
            display.thinking(f"Processing step {i+1}...")
        
        print("\nDisplay test complete. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        display.stop()
        print("Display stopped")