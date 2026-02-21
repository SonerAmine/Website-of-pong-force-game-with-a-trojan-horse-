# ===== PONG FORCE - MULTIPLAYER ROOM SYSTEM =====

import pygame
import sys
import json
import random
import string
import config

class RoomCodeMenu:
    def __init__(self):
        """Initialize room code menu"""
        pygame.init()

        # Create screen
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE + " - Multiplayer")

        # Menu state
        self.running = True
        self.selected_option = 0
        self.room_code = ""
        self.player_name = ""
        self.is_host = True  # True for create room, False for join room
        self.input_mode = ""  # "" for menu, "name" for name input, "code" for code input, "confirm" for confirmation
        
        # Colors
        self.bg_color = config.BLACK
        self.title_color = config.NEON_YELLOW
        self.selected_color = config.NEON_PINK
        self.normal_color = config.WHITE
        self.info_color = config.NEON_BLUE
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.option_font = pygame.font.Font(None, 36)
        self.input_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Active rooms (in real implementation, this would be server-side)
        self.active_rooms = {}
        
    def generate_room_code(self):
        """Generate a random 6-character room code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def run(self):
        """Run room code menu and return mode selection"""
        result = {"mode": "back"}

        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)

        # Return the result after user confirmation
        if self.input_mode == "confirm":
            if self.is_host:
                result = {"mode": "host", "code": self.room_code, "name": self.player_name}
            else:
                result = {"mode": "join", "code": self.room_code, "name": self.player_name}

        return result
    
    def handle_events(self):
        """Handle menu events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.input_mode == "":  # Main menu
                    self.handle_menu_navigation(event)
                elif self.input_mode == "name":
                    self.handle_name_input(event)
                elif self.input_mode == "code":
                    self.handle_code_input(event)
                elif self.input_mode == "confirm":
                    self.handle_confirm_input(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.input_mode == "":  # Only handle mouse in main menu
                    self.handle_mouse_click(event)
    
    def handle_menu_navigation(self, event):
        """Handle main menu navigation"""
        if event.key == pygame.K_UP or event.key == pygame.K_w:
            self.selected_option = (self.selected_option - 1) % 3
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            self.selected_option = (self.selected_option + 1) % 3
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            if self.selected_option == 0:  # Create Room
                self.is_host = True
                self.input_mode = "name"
                self.player_name = ""
                self.room_code = self.generate_room_code()
            elif self.selected_option == 1:  # Join Room
                self.is_host = False
                self.input_mode = "name"
                self.player_name = ""
                self.room_code = ""
            elif self.selected_option == 2:  # Back
                self.running = False
        elif event.key == pygame.K_ESCAPE:
            self.running = False
    
    def handle_name_input(self, event):
        """Handle player name input"""
        if event.key == pygame.K_RETURN:
            if self.player_name.strip():
                if self.is_host:
                    # Host goes directly to confirmation
                    self.input_mode = "confirm"
                else:
                    # Join needs room code first
                    self.input_mode = "code"
            return

        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]

        elif event.key == pygame.K_ESCAPE:
            self.input_mode = ""
            self.player_name = ""
            self.room_code = ""

        else:
            # Add character to name using unicode
            if event.unicode and event.unicode.isprintable() and len(self.player_name) < 15:
                self.player_name += event.unicode
    
    def handle_code_input(self, event):
        """Handle room code input"""
        if event.key == pygame.K_RETURN:
            if len(self.room_code) == 6:
                self.input_mode = "confirm"
            return

        elif event.key == pygame.K_BACKSPACE:
            self.room_code = self.room_code[:-1]

        elif event.key == pygame.K_ESCAPE:
            self.input_mode = "name"
            self.room_code = ""

        else:
            # Add character to code using unicode
            if event.unicode and len(self.room_code) < 6:
                char = event.unicode.upper()
                if char in string.ascii_uppercase + string.digits:
                    self.room_code += char

    def handle_confirm_input(self, event):
        """Handle confirmation screen input"""
        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            # Confirm and start
            self.running = False
        elif event.key == pygame.K_ESCAPE:
            # Go back to name input
            if self.is_host:
                self.input_mode = "name"
            else:
                self.input_mode = "code"
    
    def handle_mouse_click(self, event):
        """Handle mouse clicks on menu options"""
        mouse_x, mouse_y = event.pos

        # Only handle clicks in main menu
        if self.input_mode != "":
            return

        # Define button areas
        buttons = {
            "create": (config.WINDOW_WIDTH//2 - 150, 200, 300, 50),
            "join": (config.WINDOW_WIDTH//2 - 150, 270, 300, 50),
            "back": (config.WINDOW_WIDTH//2 - 150, 340, 300, 50)
        }

        # Check which button was clicked
        for button_name, (x, y, w, h) in buttons.items():
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if button_name == "create":
                    self.selected_option = 0
                    self.is_host = True
                    self.input_mode = "name"
                    self.player_name = ""
                    self.room_code = self.generate_room_code()
                elif button_name == "join":
                    self.selected_option = 1
                    self.is_host = False
                    self.input_mode = "name"
                    self.player_name = ""
                    self.room_code = ""
                elif button_name == "back":
                    self.selected_option = 2
                    self.running = False
                break
    
    def render(self):
        """Render the room code menu"""
        self.screen.fill(self.bg_color)

        if self.input_mode == "":
            # Main menu
            self.render_main_menu()
        elif self.input_mode == "confirm":
            # Confirmation screen
            self.render_confirm_screen()
        else:
            # Input screen (name or code)
            self.render_input_screen()
    
    def render_main_menu(self):
        """Render main multiplayer menu"""
        # Title
        title_text = "Multiplayer"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Menu options
        options = [
            "Create Room",
            "Join Room", 
            "Back to Main Menu"
        ]
        
        start_y = 200
        for i, option in enumerate(options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            option_surface = self.option_font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(config.WINDOW_WIDTH // 2, start_y + i * 70))
            self.screen.blit(option_surface, option_rect)
    
    def render_input_screen(self):
        """Render input screen for name or code"""
        # Title
        title = "Create Room" if self.is_host else "Join Room"
        title_surface = self.title_font.render(title, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # Name input
        name_label = "Your Name:"
        name_label_surface = self.input_font.render(name_label, True, self.normal_color)
        name_label_rect = name_label_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 180))
        self.screen.blit(name_label_surface, name_label_rect)
        
        # Name input box
        name_box = pygame.Rect(config.WINDOW_WIDTH // 2 - 150, 220, 300, 40)
        pygame.draw.rect(self.screen, self.normal_color, name_box, 2)
        name_surface = self.input_font.render(self.player_name, True, self.normal_color)
        name_rect = name_surface.get_rect(center=name_box.center)
        self.screen.blit(name_surface, name_rect)
        
        if self.is_host and self.room_code:
            # Show generated room code
            code_label = f"Room Code: {self.room_code}"
            code_label_surface = self.input_font.render(code_label, True, self.info_color)
            code_label_rect = code_label_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 300))
            self.screen.blit(code_label_surface, code_label_rect)
            
            # Code display box
            code_box = pygame.Rect(config.WINDOW_WIDTH // 2 - 100, 340, 200, 50)
            pygame.draw.rect(self.screen, self.info_color, code_box, 3)
            code_surface = self.title_font.render(self.room_code, True, self.info_color)
            code_rect = code_surface.get_rect(center=code_box.center)
            self.screen.blit(code_surface, code_rect)
            
            instructions = "Share this code with your friend!"
            inst_surface = self.small_font.render(instructions, True, config.GRAY)
            inst_rect = inst_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 420))
            self.screen.blit(inst_surface, inst_rect)
        
        elif not self.is_host:
            # Code input for joining
            if self.input_mode == "code":
                code_label = "Enter Room Code:"
                code_label_surface = self.input_font.render(code_label, True, self.normal_color)
                code_label_rect = code_label_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 280))
                self.screen.blit(code_label_surface, code_label_rect)
                
                # Code input box
                code_box = pygame.Rect(config.WINDOW_WIDTH // 2 - 100, 320, 200, 50)
                pygame.draw.rect(self.screen, self.normal_color, code_box, 2)
                code_surface = self.title_font.render(self.room_code, True, self.normal_color)
                code_rect = code_surface.get_rect(center=code_box.center)
                self.screen.blit(code_surface, code_rect)
        
        # Instructions
        instructions = [
            "Type your name and press ENTER",
            "Press ESC to go back"
        ]
        if self.is_host:
            instructions.append("Room code will be generated automatically")
        else:
            instructions.append("Enter 6-character room code")
        
        y_offset = config.WINDOW_HEIGHT - 120
        for instruction in instructions:
            inst_surface = self.small_font.render(instruction, True, config.GRAY)
            inst_rect = inst_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(inst_surface, inst_rect)
            y_offset += 25

    def render_confirm_screen(self):
        """Render confirmation screen before starting game"""
        # Title
        title = "Ready to Host!" if self.is_host else "Ready to Join!"
        title_surface = self.title_font.render(title, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)

        # Player info
        y_pos = 180

        # Player name
        name_label = f"Player: {self.player_name}"
        name_surface = self.option_font.render(name_label, True, self.info_color)
        name_rect = name_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_pos))
        self.screen.blit(name_surface, name_rect)
        y_pos += 60

        # Room code
        code_label = f"Room Code: {self.room_code}"
        code_surface = self.option_font.render(code_label, True, self.info_color)
        code_rect = code_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_pos))
        self.screen.blit(code_surface, code_rect)
        y_pos += 40

        # Big room code display
        code_box = pygame.Rect(config.WINDOW_WIDTH // 2 - 120, y_pos, 240, 60)
        pygame.draw.rect(self.screen, self.selected_color, code_box, 3)
        big_code_surface = self.title_font.render(self.room_code, True, self.selected_color)
        big_code_rect = big_code_surface.get_rect(center=code_box.center)
        self.screen.blit(big_code_surface, big_code_rect)
        y_pos += 100

        # Instructions
        if self.is_host:
            instruction = "Press ENTER to start hosting"
        else:
            instruction = "Press ENTER to join game"

        inst_surface = self.input_font.render(instruction, True, self.normal_color)
        inst_rect = inst_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_pos))
        self.screen.blit(inst_surface, inst_rect)
        y_pos += 40

        # Back instruction
        back_surface = self.small_font.render("Press ESC to go back", True, config.GRAY)
        back_rect = back_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_pos))
        self.screen.blit(back_surface, back_rect)
