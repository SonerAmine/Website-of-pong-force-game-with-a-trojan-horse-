# ===== PONG FORCE - CONTROLS CONFIGURATION =====

import pygame
import sys
import json
import os
import config

class ControlsMenu:
    def __init__(self):
        """Initialize controls configuration menu"""
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE + " - Controls")
        
        # Menu state
        self.running = True
        self.selected_option = 0
        self.editing_player = None  # None, 1, or 2
        
        # Default controls
        self.controls = {
            "player1": {
                "multiplayer": {"up": "up", "down": "down", "force": "space"},
                "vs_robot": {"up": "up", "down": "down", "force": "space"},
                "two_player_local": {"up": "up", "down": "down", "force": "space"}
            },
            "player2": {
                "multiplayer": {"up": "w", "down": "s", "force": "shift"},
                "vs_robot": {"up": "w", "down": "s", "force": "shift"},
                "two_player_local": {"up": "z", "down": "s", "force": "a"}
            }
        }
        
        # Available keys
        self.available_keys = [
            "up", "down", "left", "right", "space", "shift",
            "w", "a", "s", "d", "z", "x", "c", "v",
            "q", "e", "r", "f", "g", "h", "y", "u", "i",
            "j", "k", "l", "m", "n", "b", "o", "p"
        ]
        
        # Colors
        self.bg_color = config.BLACK
        self.title_color = config.NEON_YELLOW
        self.selected_color = config.NEON_PINK
        self.normal_color = config.WHITE
        self.info_color = config.NEON_BLUE
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.option_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Key mapping for display
        self.key_display_names = {
            "up": "UP", "down": "DOWN", "left": "LEFT", "right": "RIGHT",
            "space": "SPACE", "shift": "SHIFT", "w": "W", "a": "A",
            "s": "S", "d": "D", "z": "Z", "x": "X", "c": "C",
            "v": "V", "q": "Q", "e": "E", "r": "R", "f": "F",
            "g": "G", "h": "H", "y": "Y", "u": "U", "i": "I",
            "j": "J", "k": "K", "l": "L", "m": "M", "n": "N",
            "b": "B", "o": "O", "p": "P"
        }
        
        # Load saved controls if exists
        self.load_controls()
        
    def load_controls(self):
        """Load controls from file if exists"""
        controls_file = os.path.join(os.path.dirname(__file__), "..", "controls.json")
        if os.path.exists(controls_file):
            try:
                with open(controls_file, 'r') as f:
                    saved_controls = json.load(f)
                    self.controls.update(saved_controls)
                    print("Controls loaded from file")
            except Exception as e:
                print(f"Error loading controls: {e}")
    
    def save_controls(self):
        """Save controls to file"""
        controls_file = os.path.join(os.path.dirname(__file__), "..", "controls.json")
        try:
            with open(controls_file, 'w') as f:
                json.dump(self.controls, f, indent=2)
                print("Controls saved to file")
        except Exception as e:
            print(f"Error saving controls: {e}")
    
    def run(self):
        """Run controls menu and return when done"""
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        # Save controls before exiting
        self.save_controls()
        return True
    
    def get_option_rect(self, index):
        """Get the clickable rectangle for a main menu option"""
        start_y = 180
        option_y = start_y + index * 50
        box_width = 500
        box_height = 45
        return pygame.Rect(
            config.WINDOW_WIDTH // 2 - box_width // 2,
            option_y - box_height // 2,
            box_width,
            box_height
        )

    def handle_events(self):
        """Handle menu events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.editing_player is None:
                    # Main menu navigation
                    if event.key == pygame.K_1 or event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % 4
                    elif event.key == pygame.K_3 or event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % 4
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.selected_option == 0:  # Player 1 controls
                            self.editing_player = 1
                        elif self.selected_option == 1:  # Player 2 controls
                            self.editing_player = 2
                        elif self.selected_option == 2:  # Reset to defaults
                            self.reset_to_defaults()
                        elif self.selected_option == 3:  # Back
                            self.running = False
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                else:
                    # Editing controls - use +/- to navigate
                    if event.key == pygame.K_1 or event.key == pygame.K_LEFT:
                        self.selected_option = (self.selected_option - 1) % 3
                    elif event.key == pygame.K_3 or event.key == pygame.K_RIGHT:
                        self.selected_option = (self.selected_option + 1) % 3
                    else:
                        # Handle key assignment
                        self.handle_key_edit(event)

            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is over any option in main menu
                if self.editing_player is None:
                    mouse_pos = event.pos
                    for i in range(4):
                        if self.get_option_rect(i).collidepoint(mouse_pos):
                            self.selected_option = i
                            break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.editing_player is None:
                    # Main menu mouse click
                    mouse_pos = event.pos
                    for i in range(4):
                        if self.get_option_rect(i).collidepoint(mouse_pos):
                            self.selected_option = i
                            # Execute the action
                            if self.selected_option == 0:  # Player 1 controls
                                self.editing_player = 1
                            elif self.selected_option == 1:  # Player 2 controls
                                self.editing_player = 2
                            elif self.selected_option == 2:  # Reset to defaults
                                self.reset_to_defaults()
                            elif self.selected_option == 3:  # Back
                                self.running = False
                            break
                else:
                    # Editing mode mouse click
                    self.handle_mouse_click(event)
    
    def handle_key_edit(self, event):
        """Handle key editing for player"""
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_DELETE:
            self.editing_player = None
            return
        
        # Map pygame key to our control name
        key_name = self.pygame_key_to_name(event.key)
        if key_name and key_name in self.available_keys:
            # Check for conflicts
            if not self.is_control_allowed(key_name, self.editing_player, self.selected_option):
                print(f"Control '{key_name}' is already in use or conflicts with existing controls")
                return
            
            if self.editing_player == 1:
                # Player 1 editing (applies to all modes)
                if self.selected_option == 0:  # Up
                    self.controls["player1"]["multiplayer"]["up"] = key_name
                    self.controls["player1"]["vs_robot"]["up"] = key_name
                    self.controls["player1"]["two_player_local"]["up"] = key_name
                elif self.selected_option == 1:  # Down
                    self.controls["player1"]["multiplayer"]["down"] = key_name
                    self.controls["player1"]["vs_robot"]["down"] = key_name
                    self.controls["player1"]["two_player_local"]["down"] = key_name
                elif self.selected_option == 2:  # Force
                    self.controls["player1"]["multiplayer"]["force"] = key_name
                    self.controls["player1"]["vs_robot"]["force"] = key_name
                    self.controls["player1"]["two_player_local"]["force"] = key_name
            
            elif self.editing_player == 2:
                # Player 2 editing (only applies to two_player_local mode)
                if self.selected_option == 0:  # Up
                    self.controls["player2"]["two_player_local"]["up"] = key_name
                elif self.selected_option == 1:  # Down
                    self.controls["player2"]["two_player_local"]["down"] = key_name
                elif self.selected_option == 2:  # Force
                    self.controls["player2"]["two_player_local"]["force"] = key_name
    
    def is_control_allowed(self, key_name, player, control_index):
        """Check if a control assignment is allowed (no conflicts)"""
        # Get the control type being edited
        control_types = ["up", "down", "force"]
        control_type = control_types[control_index]
        
        # Check Player 1 controls (all modes)
        p1_controls = self.controls["player1"]
        for mode in ["multiplayer", "vs_robot", "two_player_local"]:
            if p1_controls[mode][control_type] == key_name:
                # Allow if editing Player 1 and same control type in same mode
                if player == 1:
                    continue
                else:
                    return False  # Player 2 cannot use Player 1's controls
            
            # Check if key is already used by Player 1 for any other control
            if player == 2:  # Player 2 cannot use any of Player 1's controls
                for other_control in ["up", "down", "force"]:
                    if other_control != control_type and p1_controls[mode][other_control] == key_name:
                        return False
        
        # Check Player 2 controls (only two_player_local mode matters)
        if player == 1:
            # Player 1 cannot use Player 2's controls in two_player_local mode
            p2_controls = self.controls["player2"]["two_player_local"]
            for other_control in ["up", "down", "force"]:
                if p2_controls[other_control] == key_name:
                    return False
        else:  # player == 2
            # Player 2 cannot duplicate their own controls
            p2_controls = self.controls["player2"]["two_player_local"]
            for other_control in ["up", "down", "force"]:
                if other_control != control_type and p2_controls[other_control] == key_name:
                    return False
        
        return True
    
    def pygame_key_to_name(self, key):
        """Convert pygame key to our control name"""
        key_map = {
            pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_LEFT: "left", pygame.K_RIGHT: "right",
            pygame.K_SPACE: "space", pygame.K_LSHIFT: "shift", pygame.K_RSHIFT: "shift",
            pygame.K_w: "w", pygame.K_a: "a", pygame.K_s: "s", pygame.K_d: "d",
            pygame.K_z: "z", pygame.K_x: "x", pygame.K_c: "c", pygame.K_v: "v",
            pygame.K_q: "q", pygame.K_e: "e", pygame.K_r: "r", pygame.K_f: "f",
            pygame.K_g: "g", pygame.K_h: "h", pygame.K_y: "y", pygame.K_u: "u",
            pygame.K_i: "i", pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l",
            pygame.K_m: "m", pygame.K_n: "n", pygame.K_b: "b", pygame.K_o: "o",
            pygame.K_p: "p"
        }
        return key_map.get(key, "up")  # Default to UP if not found
    
    def handle_mouse_click(self, event):
        """Handle mouse click on control buttons"""
        mouse_x, mouse_y = event.pos
        
        # Define button areas (x, y, width, height)
        buttons = {
            "player1_up": (config.WINDOW_WIDTH//2 - 150, 200, 100, 40),
            "player1_down": (config.WINDOW_WIDTH//2 - 150, 250, 100, 40),
            "player1_force": (config.WINDOW_WIDTH//2 - 150, 300, 100, 40),
            "player2_up": (config.WINDOW_WIDTH//2 + 150, 200, 100, 40),
            "player2_down": (config.WINDOW_WIDTH//2 + 150, 250, 100, 40),
            "player2_force": (config.WINDOW_WIDTH//2 + 150, 300, 100, 40)
        }
        
        # Check which button was clicked
        for button_name, (x, y, w, h) in buttons.items():
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                if self.editing_player == 1:
                    # Player 1 button clicked
                    if button_name == "player1_up":
                        self.selected_option = 0  # Up
                    elif button_name == "player1_down":
                        self.selected_option = 1  # Down
                    elif button_name == "player1_force":
                        self.selected_option = 2  # Force
                elif self.editing_player == 2:
                    # Player 2 button clicked
                    if button_name == "player2_up":
                        self.selected_option = 0  # Up
                    elif button_name == "player2_down":
                        self.selected_option = 1  # Down
                    elif button_name == "player2_force":
                        self.selected_option = 2  # Force
    
    def reset_to_defaults(self):
        """Reset controls to default values"""
        self.controls = {
            "player1": {
                "multiplayer": {"up": "up", "down": "down", "force": "space"},
                "vs_robot": {"up": "up", "down": "down", "force": "space"},
                "two_player_local": {"up": "up", "down": "down", "force": "space"}
            },
            "player2": {
                "multiplayer": {"up": "w", "down": "s", "force": "shift"},
                "vs_robot": {"up": "w", "down": "s", "force": "shift"},
                "two_player_local": {"up": "z", "down": "s", "force": "a"}
            }
        }
        print("Controls reset to defaults")
    
    def get_controls_for_mode(self, player, mode):
        """Get controls for specific player and mode"""
        return self.controls[f"player{player}"][mode]
    
    def render(self):
        """Render the controls menu"""
        self.screen.fill(self.bg_color)
        
        if self.editing_player is None:
            # Main menu
            self.render_main_menu()
        else:
            # Editing controls
            self.render_edit_menu()
    
    def render_main_menu(self):
        """Render main controls menu"""
        # Title
        title_text = "Controls Configuration"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_surface, title_rect)

        # Menu options
        options = [
            "Configure Player 1 Controls",
            "Configure Player 2 Controls",
            "Reset to Defaults",
            "Back to Main Menu"
        ]

        start_y = 180
        for i, option in enumerate(options):
            option_rect = self.get_option_rect(i)

            if i == self.selected_option:
                # Draw selection box with glow effect
                glow_surface = pygame.Surface((option_rect.width + 12, option_rect.height + 12), pygame.SRCALPHA)
                glow_color = (*self.selected_color, 60)
                pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=10)
                self.screen.blit(glow_surface, (option_rect.x - 6, option_rect.y - 6))

                # Draw selection border
                pygame.draw.rect(self.screen, self.selected_color, option_rect, 2, border_radius=8)

                # Draw indicator circle
                pygame.draw.circle(self.screen, self.selected_color,
                                 (option_rect.left - 15, option_rect.centery), 6)
                color = self.selected_color
            else:
                # Draw subtle border for non-selected items
                pygame.draw.rect(self.screen, (50, 50, 50), option_rect, 1, border_radius=8)
                color = self.normal_color

            option_surface = self.option_font.render(option, True, color)
            option_text_rect = option_surface.get_rect(center=option_rect.center)
            self.screen.blit(option_surface, option_text_rect)

        # Instructions
        hint_text = "Arrow Keys / Mouse to navigate  |  ENTER / Click to select  |  ESC to go back"
        hint_surface = pygame.font.Font(None, 22).render(hint_text, True, config.GRAY)
        hint_rect = hint_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 40))
        self.screen.blit(hint_surface, hint_rect)
    
    def render_edit_menu(self):
        """Render control editing menu"""
        player_text = f"Player {self.editing_player} Controls"
        title_surface = self.title_font.render(player_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 60))
        self.screen.blit(title_surface, title_rect)
        
        # Show behavior explanation
        if self.editing_player == 1:
            behavior_text = "Changes apply to ALL modes (vs Robot, 2-Player, Multiplayer)"
            behavior_color = config.NEON_BLUE
        else:
            behavior_text = "Changes apply ONLY to 2-Player Local mode"
            behavior_color = config.NEON_PINK
        
        behavior_surface = self.small_font.render(behavior_text, True, behavior_color)
        behavior_rect = behavior_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 90))
        self.screen.blit(behavior_surface, behavior_rect)
        
        # Show current controls for different modes
        if self.editing_player == 1:
            # Player 1 sees all modes
            modes = ["multiplayer", "vs_robot", "two_player_local"]
            mode_names = ["Multiplayer", "vs Robot", "2-Player Local"]
        else:
            # Player 2 sees only 2-Player Local mode
            modes = ["two_player_local"]
            mode_names = ["2-Player Local"]
        
        start_y = 130
        for mode_idx, (mode, mode_name) in enumerate(zip(modes, mode_names)):
            controls = self.controls[f"player{self.editing_player}"][mode]
            
            # Mode name
            mode_surface = self.option_font.render(mode_name + ":", True, self.info_color)
            mode_rect = mode_surface.get_rect(center=(config.WINDOW_WIDTH // 2, start_y + mode_idx * 100))
            self.screen.blit(mode_surface, mode_rect)
            
            # Controls with highlighting for selected control
            up_key = self.key_display_names.get(controls["up"], controls["up"].upper())
            down_key = self.key_display_names.get(controls["down"], controls["down"].upper())
            force_key = self.key_display_names.get(controls["force"], controls["force"].upper())
            
            # Highlight selected control
            if self.selected_option == 0:  # Up selected
                up_color = self.selected_color
                down_color = self.normal_color
                force_color = self.normal_color
            elif self.selected_option == 1:  # Down selected
                up_color = self.normal_color
                down_color = self.selected_color
                force_color = self.normal_color
            else:  # Force selected
                up_color = self.normal_color
                down_color = self.normal_color
                force_color = self.selected_color
            
            # Draw controls with different colors
            controls_text = f"Up: {up_key}  Down: {down_key}  Force: {force_key}"
            
            # Create separate surfaces for each control to apply different colors
            up_text_surface = self.small_font.render(f"Up: {up_key}", True, up_color)
            down_text_surface = self.small_font.render(f"Down: {down_key}", True, down_color)
            force_text_surface = self.small_font.render(f"Force: {force_key}", True, force_color)
            
            # Calculate positions
            total_width = up_text_surface.get_width() + down_text_surface.get_width() + force_text_surface.get_width() + 40
            start_x = config.WINDOW_WIDTH // 2 - total_width // 2
            
            self.screen.blit(up_text_surface, (start_x, start_y + 30 + mode_idx * 100))
            self.screen.blit(down_text_surface, (start_x + up_text_surface.get_width() + 20, start_y + 30 + mode_idx * 100))
            self.screen.blit(force_text_surface, (start_x + up_text_surface.get_width() + down_text_surface.get_width() + 40, start_y + 30 + mode_idx * 100))
        
        # Instructions with conflict warning
        instructions = [
            "Use LEFT/RIGHT to select control to change",
            "Press any key to assign to selected control",
            "Controls cannot be duplicated between players",
            "Press ESC to finish editing"
        ]
        
        inst_y = config.WINDOW_HEIGHT - 140
        for i, instruction in enumerate(instructions):
            color = config.NEON_PINK if i == 2 else config.GRAY  # Highlight conflict warning
            inst_surface = self.small_font.render(instruction, True, color)
            inst_rect = inst_surface.get_rect(center=(config.WINDOW_WIDTH // 2, inst_y))
            self.screen.blit(inst_surface, inst_rect)
            inst_y += 30
