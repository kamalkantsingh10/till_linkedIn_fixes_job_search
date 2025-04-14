import pygame
import sys
import threading
import queue
import time
from typing import List, Dict, Any, Tuple, Optional
import os

class AgentDisplay:
    """
    A simplified version of the AgentDisplay that works reliably on Ubuntu.
    """
    
    def __init__(self, width=1200, height=800):
        # Initialize pygame with minimal settings
        pygame.init()
        print(f"Using SDL video driver: {pygame.display.get_driver()}")
        
        # Constants
        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        self.PADDING = 10
        self.FONT_SIZE = 18
        self.TITLE_FONT_SIZE = 24
        
        # Screen titles
        self.SCREEN_TITLES = [
            "Input",
            "Steps (Executed & Planned)",
            "Thinking Process",
            "Function Calls & Outputs",
            "Errors"
        ]
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (100, 100, 100)
        self.LIGHT_BLUE = (200, 220, 255)
        self.LIGHT_GREEN = (200, 255, 220)
        self.LIGHT_YELLOW = (255, 255, 200)
        self.LIGHT_RED = (255, 200, 200)
        self.LIGHT_PURPLE = (230, 200, 255)
        self.SCREEN_COLORS = [
            self.LIGHT_BLUE,    # Input
            self.LIGHT_GREEN,   # Steps
            self.LIGHT_YELLOW,  # Thinking
            self.LIGHT_PURPLE,  # Function Calls
            self.LIGHT_RED      # Errors
        ]
        
        # Initialize screen with basic settings
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Agent Framework UI")
        
        # Fonts - try Ubuntu fonts first, then fallback
        try:
            try:
                self.font = pygame.font.SysFont("Ubuntu", self.FONT_SIZE)
                self.title_font = pygame.font.SysFont("Ubuntu", self.TITLE_FONT_SIZE, bold=True)
            except:
                self.font = pygame.font.SysFont(None, self.FONT_SIZE)
                self.title_font = pygame.font.SysFont(None, self.TITLE_FONT_SIZE, bold=True)
        except:
            print("Error initializing fonts")
            self.font = None
            self.title_font = None
        
        # Screen Rects
        screen_width = (self.SCREEN_WIDTH - self.PADDING * 6) // 2
        screen_height = (self.SCREEN_HEIGHT - self.PADDING * 4) // 2
        
        self.screen_rects = [
            pygame.Rect(self.PADDING, self.PADDING, screen_width, screen_height),  # Input
            pygame.Rect(self.PADDING * 2 + screen_width, self.PADDING, screen_width, screen_height),  # Steps
            pygame.Rect(self.PADDING, self.PADDING * 2 + screen_height, screen_width, screen_height),  # Thinking
            pygame.Rect(self.PADDING * 2 + screen_width, self.PADDING * 2 + screen_height, screen_width, screen_height),  # Function Calls
            pygame.Rect(self.PADDING * 3 + screen_width * 2, self.PADDING, screen_width // 2, self.SCREEN_HEIGHT - self.PADDING * 2)  # Errors
        ]
        
        # Content and scrolling state for each screen
        self.screen_content = ["", "", "", "", ""]
        self.scroll_positions = [0, 0, 0, 0, 0]
        self.max_scroll_positions = [0, 0, 0, 0, 0]
        self.active_screen = 0
        self.scroll_amount = 20
        
        # State data
        self.input_text = ""
        self.steps_executed = []
        self.steps_planned = []
        self.thinking_lines = []
        self.function_calls = []
        self.errors = []
        
        # Main thread control
        self.running = False
        
        # Queue for UI updates to handle in main thread
        self.ui_queue = queue.Queue()
        
    def start(self):
        """Start the main loop"""
        if not self.running:
            self.running = True
            self._main_loop()
            
    def stop(self):
        """Stop the main loop"""
        self.running = False
        pygame.quit()
    
    def _main_loop(self):
        """Main loop running in the same thread"""
        clock = pygame.time.Clock()
        
        while self.running:
            # Process UI queue
            self._process_queue()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_UP:
                        self._scroll(self.active_screen, -1)
                    elif event.key == pygame.K_DOWN:
                        self._scroll(self.active_screen, 1)
                    elif event.key == pygame.K_PAGEUP:
                        self._scroll(self.active_screen, -5)
                    elif event.key == pygame.K_PAGEDOWN:
                        self._scroll(self.active_screen, 5)
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        self.active_screen = event.key - pygame.K_1
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        for i, rect in enumerate(self.screen_rects):
                            if rect.collidepoint(event.pos):
                                self.active_screen = i
                                self._scroll(i, -1)
                                break
                    elif event.button == 5:  # Scroll down
                        for i, rect in enumerate(self.screen_rects):
                            if rect.collidepoint(event.pos):
                                self.active_screen = i
                                self._scroll(i, 1)
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click
                        for i, rect in enumerate(self.screen_rects):
                            if rect.collidepoint(event.pos):
                                self.active_screen = i
                                break
            
            # Update display
            self._update_display()
            
            # Cap at 30 FPS
            clock.tick(30)
            
    def _process_queue(self):
        """Process commands from the queue"""
        try:
            while not self.ui_queue.empty():
                cmd, args = self.ui_queue.get_nowait()
                if cmd == 'input':
                    self.input_text = args
                    self.screen_content[0] = f"User Input:\n\n{args}"
                elif cmd == 'steps':
                    executed, planned = args
                    self.steps_executed = executed
                    self.steps_planned = planned
                    self._update_steps_display()
                elif cmd == 'thinking':
                    self.thinking_lines.append(args)
                    self.screen_content[2] = "\n\n".join(self.thinking_lines)
                elif cmd == 'function':
                    name, params, result = args
                    self._add_function_call(name, params, result)
                elif cmd == 'error':
                    self.errors.append(args)
                    self.screen_content[4] = "\n\n".join(self.errors)
                self.ui_queue.task_done()
        except Exception as e:
            print(f"Error processing UI queue: {e}")
    
    def _update_steps_display(self):
        """Update the steps display with current executed and planned steps"""
        steps_text = "Executed Steps:\n"
        for i, (step, result) in enumerate(self.steps_executed):
            steps_text += f"{i+1}. {step}\n   Result: {result}\n\n"
        
        steps_text += "\nPlanned Steps:\n"
        for i, step in enumerate(self.steps_planned):
            steps_text += f"{i+1}. {step}\n"
        
        self.screen_content[1] = steps_text
    
    def _add_function_call(self, function_name, params, result):
        """Add a function call to the function calls display"""
        formatted_call = f"Function: {function_name}\n"
        formatted_call += "Parameters:\n"
        for k, v in params.items():
            formatted_call += f"  {k}: {v}\n"
        formatted_call += f"Result: {result}\n"
        formatted_call += "-" * 40 + "\n"
        
        self.function_calls.append(formatted_call)
        self.screen_content[3] = "\n".join(self.function_calls)
    
    def _scroll(self, screen_index, amount):
        """Scroll a screen up or down"""
        self.scroll_positions[screen_index] += amount * self.scroll_amount
        if self.scroll_positions[screen_index] < 0:
            self.scroll_positions[screen_index] = 0
        elif self.scroll_positions[screen_index] > self.max_scroll_positions[screen_index]:
            self.scroll_positions[screen_index] = self.max_scroll_positions[screen_index]
    
    def _update_display(self):
        """Update the display"""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw each content screen
        for i, rect in enumerate(self.screen_rects):
            # Draw background
            pygame.draw.rect(self.screen, self.SCREEN_COLORS[i], rect)
            pygame.draw.rect(self.screen, self.DARK_GRAY, rect, 2)
            
            # Draw title
            title_surface = self.title_font.render(self.SCREEN_TITLES[i], True, self.BLACK)
            self.screen.blit(title_surface, (rect.x + 10, rect.y + 5))
            
            # Draw content with scrolling
            content = self.screen_content[i]
            if content:
                self._render_scrollable_text(content, rect, i)
            
            # Draw scroll indicators if needed
            if self.max_scroll_positions[i] > 0:
                pygame.draw.rect(self.screen, self.DARK_GRAY, (rect.right - 15, rect.y + 30, 10, rect.height - 40))
                scroll_height = max(30, (rect.height - 40) * (rect.height - 40) / (self.max_scroll_positions[i] + rect.height - 40))
                scroll_pos = (rect.height - 40 - scroll_height) * (self.scroll_positions[i] / self.max_scroll_positions[i]) if self.max_scroll_positions[i] > 0 else 0
                pygame.draw.rect(self.screen, self.WHITE, (rect.right - 15, rect.y + 30 + scroll_pos, 10, scroll_height))
        
        # Simple update using the most basic update method
        pygame.display.update()
    
    def _render_scrollable_text(self, text, rect, screen_index):
        """Render scrollable text in a rect"""
        if self.font is None:
            return
            
        # Split text into lines (with wrapping)
        lines = []
        for paragraph in text.split('\n'):
            if not paragraph:
                lines.append('')
            else:
                # Simple wrapping by characters (can be improved)
                max_chars = (rect.width - 20) // (self.FONT_SIZE // 2)
                while paragraph:
                    if len(paragraph) <= max_chars:
                        lines.append(paragraph)
                        paragraph = ''
                    else:
                        # Find a good breaking point
                        break_point = max_chars
                        while break_point > 0 and paragraph[break_point] != ' ':
                            break_point -= 1
                        if break_point == 0:  # No space found, just cut
                            break_point = max_chars
                        
                        lines.append(paragraph[:break_point])
                        paragraph = paragraph[break_point:].lstrip()
        
        # Calculate max scroll
        total_height = len(lines) * (self.FONT_SIZE + 2)
        content_height = rect.height - 40  # Exclude title area
        self.max_scroll_positions[screen_index] = max(0, total_height - content_height)
        
        # Clamp scroll position
        self.scroll_positions[screen_index] = max(0, min(self.scroll_positions[screen_index], self.max_scroll_positions[screen_index]))
        
        # Render visible lines
        start_line = self.scroll_positions[screen_index] // (self.FONT_SIZE + 2)
        visible_lines = min(len(lines) - start_line, content_height // (self.FONT_SIZE + 2) + 1)
        
        for i in range(visible_lines):
            if start_line + i < len(lines):
                line_surface = self.font.render(lines[start_line + i], True, self.BLACK)
                self.screen.blit(line_surface, (rect.x + 10, rect.y + 30 + i * (self.FONT_SIZE + 2) - self.scroll_positions[screen_index] % (self.FONT_SIZE + 2)))
    
    # Public interface methods for the agent to call
    
    def input(self, text):
        """Update the input display"""
        self.ui_queue.put(('input', text))
    
    def update_steps(self, executed, planned):
        """Update the steps display"""
        self.ui_queue.put(('steps', (executed, planned)))
    
    def thinking(self, text):
        """Add a line to the thinking process display"""
        self.ui_queue.put(('thinking', text))
    
    def function(self, name, params, result):
        """Add a function call to the function calls display"""
        self.ui_queue.put(('function', (name, params, result)))
    
    def error(self, text):
        """Add an error to the errors display"""
        self.ui_queue.put(('error', text))

# Example usage
if __name__ == "__main__":
    display = AgentDisplay()
    
    # Add some example data
    display.input("Example user query about data analysis")
    display.thinking("Analyzing the user's question...")
    display.thinking("Determining appropriate analysis steps...")
    display.update_steps(
        [("Parse user query", "Identified request for data visualization")], 
        ["Retrieve data", "Clean data", "Create visualization"]
    )
    display.function("retrieve_data", {"source": "database"}, "Retrieved 1000 records")
    
    # Start the display - this will block until the window is closed
    display.start()