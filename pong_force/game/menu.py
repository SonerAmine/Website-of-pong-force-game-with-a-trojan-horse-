# ===== PONG FORCE - GRAPHICAL MENU =====

import pygame
import sys
import config

class GoalSelectionMenu:
    def __init__(self):
        """Initialize goal selection menu"""
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE + " - Select Match Goals")
        
        # Menu state
        self.running = True
        self.selected_option = 1  # Default to 5 goals
        self.goal_options = [3, 5, 7, 10]
        
        # Colors
        self.bg_color = config.BLACK
        self.title_color = config.NEON_YELLOW
        self.selected_color = config.NEON_PINK
        self.normal_color = config.WHITE
        
        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.option_font = pygame.font.Font(None, 48)
        self.info_font = pygame.font.Font(None, 24)
        
        # Clock
        self.clock = pygame.time.Clock()
        
    def run(self):
        """Run goal selection menu and return selected goals"""
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.goal_options[self.selected_option]
    
    def get_goal_rect(self, index):
        """Get the clickable rectangle for a goal option"""
        start_x = config.WINDOW_WIDTH // 2 - (len(self.goal_options) * 120) // 2
        x = start_x + index * 120
        y = config.WINDOW_HEIGHT // 2
        return pygame.Rect(x - 40, y - 30, 80, 60)

    def handle_events(self):
        """Handle menu events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.selected_option = -1
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_option = (self.selected_option - 1) % len(self.goal_options)

                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_option = (self.selected_option + 1) % len(self.goal_options)

                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.running = False

                elif event.key == pygame.K_ESCAPE:
                    self.selected_option = -1
                    self.running = False

            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is over any goal option
                mouse_pos = event.pos
                for i in range(len(self.goal_options)):
                    if self.get_goal_rect(i).collidepoint(mouse_pos):
                        self.selected_option = i
                        break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    for i in range(len(self.goal_options)):
                        if self.get_goal_rect(i).collidepoint(mouse_pos):
                            self.selected_option = i
                            self.running = False
                            break
    
    def render(self):
        """Render the menu"""
        self.screen.fill(self.bg_color)
        
        # Title
        title_text = "Select Match Goals"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Goal options
        start_x = config.WINDOW_WIDTH // 2 - (len(self.goal_options) * 120) // 2
        for i, goals in enumerate(self.goal_options):
            x = start_x + i * 120
            y = config.WINDOW_HEIGHT // 2
            
            # Draw box
            box_rect = pygame.Rect(x - 40, y - 30, 80, 60)
            if i == self.selected_option:
                pygame.draw.rect(self.screen, self.selected_color, box_rect, 3, border_radius=10)
                # Draw glow effect
                glow_surface = pygame.Surface((100, 80), pygame.SRCALPHA)
                glow_color = (*self.selected_color, 50)
                pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=15)
                self.screen.blit(glow_surface, (box_rect.x - 10, box_rect.y - 10))
            else:
                pygame.draw.rect(self.screen, self.normal_color, box_rect, 2, border_radius=10)
            
            # Draw goal number
            goal_text = str(goals)
            goal_surface = self.option_font.render(goal_text, True, 
                                              self.selected_color if i == self.selected_option else self.normal_color)
            goal_rect = goal_surface.get_rect(center=(x, y))
            self.screen.blit(goal_surface, goal_rect)
        
        # Instructions
        info_lines = [
            "Use LEFT/RIGHT or A/D to select",
            "Press ENTER or SPACE to confirm",
            "Press ESC to go back"
        ]
        
        y_offset = config.WINDOW_HEIGHT - 100
        for line in info_lines:
            info_surface = self.info_font.render(line, True, config.GRAY)
            info_rect = info_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(info_surface, info_rect)
            y_offset += 30


class GameMenu:
    def __init__(self):
        """Initialize the game menu"""
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE + " - Menu")
        
        # Menu state
        self.running = True
        self.selected_option = 0
        self.menu_options = [
            "Play vs Robot",
            "Play 2-Player Local",
            "Configure Controls",
            "Player Statistics",
            "Multiplayer Room"
        ]
        
        # Colors
        self.bg_color = config.BLACK
        self.title_color = config.NEON_YELLOW
        self.selected_color = config.NEON_PINK
        self.normal_color = config.WHITE
        self.subtitle_color = config.NEON_BLUE
        
        # Fonts
        self.title_font = pygame.font.Font(None, 96)
        self.option_font = pygame.font.Font(None, 42)
        self.subtitle_font = pygame.font.Font(None, 28)
        
        # Animation
        self.glow_alpha = 0
        self.glow_direction = 1
        self.pulse_timer = 0
        self.particle_timer = 0
        
        # Background particles
        self.background_particles = []
        self.init_particles()
        
        # Selection glow
        self.selection_glow = 0
        
        # Clock
        self.clock = pygame.time.Clock()
        
    def init_particles(self):
        """Initialize background particles"""
        import random
        for _ in range(50):
            particle = {
                'x': random.uniform(0, config.WINDOW_WIDTH),
                'y': random.uniform(0, config.WINDOW_HEIGHT),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(30, 100),
                'color': random.choice([config.NEON_BLUE, config.NEON_PINK, config.NEON_YELLOW])
            }
            self.background_particles.append(particle)
        
    def run(self):
        """Run the menu and return selected option"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.selected_option
    
    def get_option_rect(self, index):
        """Get the clickable rectangle for a menu option"""
        start_y = 220
        spacing = 65
        option_y = start_y + index * spacing
        box_width = 500
        box_height = 55
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
                self.selected_option = -1
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)

                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)

                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.running = False

                elif event.key == pygame.K_ESCAPE:
                    self.selected_option = -1  # Exit/Cancel
                    self.running = False

            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is over any option
                mouse_pos = event.pos
                for i in range(len(self.menu_options)):
                    if self.get_option_rect(i).collidepoint(mouse_pos):
                        self.selected_option = i
                        break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = event.pos
                    for i in range(len(self.menu_options)):
                        if self.get_option_rect(i).collidepoint(mouse_pos):
                            self.selected_option = i
                            self.running = False
                            break
    
    def update(self):
        """Update menu animations"""
        import random
        import math
        
        # Pulse effect for title
        self.glow_alpha += self.glow_direction * 3
        if self.glow_alpha >= 255:
            self.glow_alpha = 255
            self.glow_direction = -1
        elif self.glow_alpha <= 100:
            self.glow_alpha = 100
            self.glow_direction = 1
        
        # Pulse timer for smoother animations
        self.pulse_timer += 0.05
        
        # Selection glow
        self.selection_glow = 0.5 + 0.5 * math.sin(self.pulse_timer * 3)
        
        # Update background particles
        for particle in self.background_particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = config.WINDOW_WIDTH
            elif particle['x'] > config.WINDOW_WIDTH:
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = config.WINDOW_HEIGHT
            elif particle['y'] > config.WINDOW_HEIGHT:
                particle['y'] = 0
    
    def render(self):
        """Render the menu"""
        # Clear screen with dark gradient
        self.screen.fill(self.bg_color)

        # Draw background particles
        self.draw_background_particles()

        # Draw decorative elements
        self.draw_decorative_elements()

        # Draw title with glow effect
        self.draw_title()

        # Draw subtitle
        self.draw_subtitle()

        # Draw menu options
        self.draw_options()

        # Draw version info
        self.draw_version_info()
    
    def draw_background_particles(self):
        """Draw animated background particles"""
        for particle in self.background_particles:
            color = particle['color']
            alpha = int(particle['alpha'])
            
            # Create particle surface
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            particle_color = (*color, alpha)
            pygame.draw.circle(particle_surface, particle_color, 
                             (int(particle['size']), int(particle['size'])), 
                             int(particle['size']))
            
            # Blit to screen
            self.screen.blit(particle_surface, 
                           (int(particle['x'] - particle['size']), 
                            int(particle['y'] - particle['size'])))
    
    def draw_title(self):
        """Draw the game title with enhanced glow effect"""
        import math
        title_text = "PONG FORCE"

        # Draw shadow for depth
        shadow_offset = 4
        shadow_surface = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(config.WINDOW_WIDTH // 2 + shadow_offset, 100 + shadow_offset))
        self.screen.blit(shadow_surface, shadow_rect)

        # Draw clean glow background using a single layer
        pulse = 0.7 + 0.3 * math.sin(self.pulse_timer * 2)
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 100))

        # Create a soft glow effect
        glow_surface = pygame.Surface((title_rect.width + 60, title_rect.height + 60), pygame.SRCALPHA)
        glow_color = (*self.title_color, int(30 * pulse))
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=30)
        self.screen.blit(glow_surface, (title_rect.x - 30, title_rect.y - 30))

        # Draw the main title text (crisp and clean)
        self.screen.blit(title_surface, title_rect)
    
    def draw_subtitle(self):
        """Draw subtitle with glow"""
        import math
        subtitle_text = "Smash. Push. Win."

        # Glow effect
        pulse = 0.6 + 0.4 * math.sin(self.pulse_timer * 1.5)
        glow_surface = self.subtitle_font.render(subtitle_text, True, self.subtitle_color)
        glow_surface.set_alpha(int(100 * pulse))
        glow_rect = glow_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 160))

        # Draw single glow layer
        for offset in [(2, 2), (-2, -2)]:
            glow_pos = glow_rect.copy()
            glow_pos.x += offset[0]
            glow_pos.y += offset[1]
            self.screen.blit(glow_surface, glow_pos)

        # Main text
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_options(self):
        """Draw menu options with enhanced effects"""
        import math

        start_y = 220
        spacing = 65

        for i, option in enumerate(self.menu_options):
            option_y = start_y + i * spacing
            option_rect = self.get_option_rect(i)

            # Choose color and effects based on selection
            if i == self.selected_option:
                color = self.selected_color

                # Outer glow
                glow_alpha = int(80 * self.selection_glow)
                glow_surface = pygame.Surface((option_rect.width + 16, option_rect.height + 16), pygame.SRCALPHA)
                glow_color = (*self.selected_color, glow_alpha)
                pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=12)
                self.screen.blit(glow_surface, (option_rect.x - 8, option_rect.y - 8))

                # Main box with gradient-like effect
                pygame.draw.rect(self.screen, self.selected_color, option_rect, 3, border_radius=10)

                # Draw animated indicator on the left
                pulse_size = 6 + int(3 * math.sin(self.pulse_timer * 5))
                indicator_x = option_rect.left - 25
                pygame.draw.circle(
                    self.screen,
                    self.selected_color,
                    (indicator_x, option_y),
                    pulse_size
                )

                # Right arrow indicator
                arrow_x = option_rect.right + 15
                pygame.draw.polygon(
                    self.screen,
                    self.selected_color,
                    [(arrow_x, option_y - 8), (arrow_x + 12, option_y), (arrow_x, option_y + 8)]
                )
            else:
                color = self.normal_color
                # Draw subtle border for non-selected items
                pygame.draw.rect(self.screen, (50, 50, 50), option_rect, 1, border_radius=10)

            # Render option text
            option_surface = self.option_font.render(option, True, color)
            option_text_rect = option_surface.get_rect(center=(config.WINDOW_WIDTH // 2, option_y))
            self.screen.blit(option_surface, option_text_rect)

        # Draw control hints at bottom
        self.draw_controls_hint()
    
    def draw_controls(self):
        """Draw control hints"""
        hints = [
            "Use Arrow Keys or W/S to navigate",
            "Press ENTER or SPACE to select",
            "Press ESC to exit"
        ]

        y_offset = config.WINDOW_HEIGHT - 100
        for hint in hints:
            hint_surface = self.subtitle_font.render(hint, True, config.GRAY)
            hint_rect = hint_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(hint_surface, hint_rect)
            y_offset += 25

    def draw_controls_hint(self):
        """Draw compact control hints at bottom of screen"""
        hint_text = "Arrow Keys / Mouse to navigate  |  ENTER / Click to select  |  ESC to exit"
        hint_surface = pygame.font.Font(None, 22).render(hint_text, True, config.GRAY)
        hint_rect = hint_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 30))
        self.screen.blit(hint_surface, hint_rect)

    def draw_decorative_elements(self):
        """Draw decorative lines and elements for professional look"""
        import math

        # Top decorative line with glow
        line_y = 50
        pulse = 0.5 + 0.5 * math.sin(self.pulse_timer)
        line_color = (*config.NEON_BLUE, int(100 + 50 * pulse))

        # Create glowing line surface
        line_surface = pygame.Surface((config.WINDOW_WIDTH, 4), pygame.SRCALPHA)
        pygame.draw.rect(line_surface, line_color, line_surface.get_rect())
        self.screen.blit(line_surface, (0, line_y))

        # Corner accents (top)
        corner_size = 40
        accent_thickness = 3

        # Top-left corner
        pygame.draw.line(self.screen, config.NEON_PINK, (20, 20), (20 + corner_size, 20), accent_thickness)
        pygame.draw.line(self.screen, config.NEON_PINK, (20, 20), (20, 20 + corner_size), accent_thickness)

        # Top-right corner
        pygame.draw.line(self.screen, config.NEON_PINK, (config.WINDOW_WIDTH - 20, 20),
                        (config.WINDOW_WIDTH - 20 - corner_size, 20), accent_thickness)
        pygame.draw.line(self.screen, config.NEON_PINK, (config.WINDOW_WIDTH - 20, 20),
                        (config.WINDOW_WIDTH - 20, 20 + corner_size), accent_thickness)

        # Bottom decorative line
        bottom_line_y = config.WINDOW_HEIGHT - 60
        line_color_bottom = (*config.NEON_YELLOW, int(80 + 40 * pulse))
        line_surface_bottom = pygame.Surface((config.WINDOW_WIDTH, 3), pygame.SRCALPHA)
        pygame.draw.rect(line_surface_bottom, line_color_bottom, line_surface_bottom.get_rect())
        self.screen.blit(line_surface_bottom, (0, bottom_line_y))

        # Side accent bars
        for i in range(3):
            y_pos = 200 + i * 150
            bar_alpha = int(30 + 20 * math.sin(self.pulse_timer + i))

            # Left bar
            left_bar = pygame.Surface((5, 80), pygame.SRCALPHA)
            pygame.draw.rect(left_bar, (*config.NEON_BLUE, bar_alpha), left_bar.get_rect())
            self.screen.blit(left_bar, (10, y_pos))

            # Right bar
            right_bar = pygame.Surface((5, 80), pygame.SRCALPHA)
            pygame.draw.rect(right_bar, (*config.NEON_PINK, bar_alpha), right_bar.get_rect())
            self.screen.blit(right_bar, (config.WINDOW_WIDTH - 15, y_pos))

    def draw_version_info(self):
        """Draw version info in corner"""
        version_font = pygame.font.Font(None, 18)
        version_text = f"v{config.VERSION}"
        version_surface = version_font.render(version_text, True, (80, 80, 80))
        version_rect = version_surface.get_rect(bottomright=(config.WINDOW_WIDTH - 20, config.WINDOW_HEIGHT - 10))
        self.screen.blit(version_surface, version_rect)


class HostInputDialog:
    """Dialog to get server IP address for client connection"""
    
    def __init__(self, default_host=""):
        """Initialize the input dialog
        
        Args:
            default_host (str): Default server IP address
        """
        self.screen = pygame.display.get_surface()
        self.running = True
        self.input_text = default_host if default_host and default_host != "0.0.0.0" else ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 20)
        self.clock = pygame.time.Clock()
        
    def run(self):
        """Run the input dialog and return entered IP address"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        # Return the entered IP or None if cancelled
        return self.input_text if self.input_text else None
    
    def handle_events(self):
        """Handle input dialog events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.input_text = config.SERVER_IP
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.running = False
                
                elif event.key == pygame.K_ESCAPE:
                    self.input_text = config.SERVER_IP
                    self.running = False
                
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                
                else:
                    # Add character to input
                    if event.unicode.isprintable():
                        self.input_text += event.unicode
    
    def update(self):
        """Update cursor blinking"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink every 0.5 seconds
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def render(self):
        """Render the input dialog"""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(config.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        dialog_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 250,
            config.WINDOW_HEIGHT // 2 - 100,
            500,
            200
        )
        pygame.draw.rect(self.screen, config.DARK_GRAY, dialog_rect)
        pygame.draw.rect(self.screen, config.NEON_BLUE, dialog_rect, 3)
        
        # Draw title
        title_surface = self.title_font.render("Enter Server IP", True, config.NEON_YELLOW)
        title_rect = title_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 60)
        )
        self.screen.blit(title_surface, title_rect)
        
        # Draw input box
        input_box = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 200,
            config.WINDOW_HEIGHT // 2 - 10,
            400,
            40
        )
        pygame.draw.rect(self.screen, config.BLACK, input_box)
        pygame.draw.rect(self.screen, config.NEON_PINK, input_box, 2)
        
        # Draw input text
        input_surface = self.font.render(self.input_text, True, config.WHITE)
        self.screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))
        
        # Draw cursor
        if self.cursor_visible:
            cursor_x = input_box.x + 10 + input_surface.get_width()
            pygame.draw.line(
                self.screen,
                config.WHITE,
                (cursor_x, input_box.y + 5),
                (cursor_x, input_box.y + 35),
                2
            )
        
        # Draw hints
        hints = [
            "Enter the server's PUBLIC IP address",
            "Example: 192.168.1.100 (local) or 123.456.789.0 (internet)",
            "Press ENTER to connect, ESC to cancel"
        ]
        
        y_pos = config.WINDOW_HEIGHT // 2 + 60
        for i, hint in enumerate(hints):
            hint_surface = self.small_font.render(hint, True, config.GRAY)
            hint_rect = hint_surface.get_rect(
                center=(config.WINDOW_WIDTH // 2, y_pos + i * 25)
            )
            self.screen.blit(hint_surface, hint_rect)


class ErrorDialog:
    """Dialog to display error messages"""
    
    def __init__(self, title, message):
        """Initialize the error dialog
        
        Args:
            title (str): Error title
            message (str): Error message
        """
        self.screen = pygame.display.get_surface()
        self.title = title
        self.message = message
        self.running = True
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        
    def run(self):
        """Run the error dialog"""
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
    
    def handle_events(self):
        """Handle error dialog events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE]:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if OK button was clicked
                button_rect = pygame.Rect(
                    config.WINDOW_WIDTH // 2 - 60,
                    config.WINDOW_HEIGHT // 2 + 180,
                    120,
                    40
                )
                if button_rect.collidepoint(event.pos):
                    self.running = False
    
    def render(self):
        """Render the error dialog"""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(config.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        dialog_width = 700
        dialog_height = 400
        dialog_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - dialog_width // 2,
            config.WINDOW_HEIGHT // 2 - dialog_height // 2,
            dialog_width,
            dialog_height
        )
        pygame.draw.rect(self.screen, config.DARK_GRAY, dialog_rect, border_radius=10)
        pygame.draw.rect(self.screen, config.NEON_PINK, dialog_rect, 3, border_radius=10)
        
        # Draw error icon (X symbol)
        icon_center_x = config.WINDOW_WIDTH // 2
        icon_center_y = config.WINDOW_HEIGHT // 2 - 140
        icon_size = 30
        pygame.draw.line(
            self.screen, config.NEON_PINK,
            (icon_center_x - icon_size, icon_center_y - icon_size),
            (icon_center_x + icon_size, icon_center_y + icon_size),
            5
        )
        pygame.draw.line(
            self.screen, config.NEON_PINK,
            (icon_center_x + icon_size, icon_center_y - icon_size),
            (icon_center_x - icon_size, icon_center_y + icon_size),
            5
        )
        
        # Draw title
        title_surface = self.title_font.render(self.title, True, config.NEON_PINK)
        title_rect = title_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 90)
        )
        self.screen.blit(title_surface, title_rect)
        
        # Draw message (multi-line support)
        message_lines = self.message.split('\n')
        y_offset = config.WINDOW_HEIGHT // 2 - 40
        max_width = dialog_width - 40
        
        for line in message_lines:
            # Wrap long lines
            words = line.split(' ')
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                test_surface = self.small_font.render(test_line, True, config.WHITE)
                
                if test_surface.get_width() > max_width and current_line:
                    # Render current line and start new one
                    line_surface = self.small_font.render(current_line, True, config.WHITE)
                    line_rect = line_surface.get_rect(
                        center=(config.WINDOW_WIDTH // 2, y_offset)
                    )
                    self.screen.blit(line_surface, line_rect)
                    y_offset += 25
                    current_line = word + " "
                else:
                    current_line = test_line
            
            # Render remaining text
            if current_line:
                line_surface = self.small_font.render(current_line, True, config.WHITE)
                line_rect = line_surface.get_rect(
                    center=(config.WINDOW_WIDTH // 2, y_offset)
                )
                self.screen.blit(line_surface, line_rect)
                y_offset += 30
        
        # Draw OK button
        button_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 60,
            config.WINDOW_HEIGHT // 2 + 180,
            120,
            40
        )
        
        # Check hover
        mouse_pos = pygame.mouse.get_pos()
        is_hover = button_rect.collidepoint(mouse_pos)
        
        button_color = config.NEON_BLUE if is_hover else config.DARK_GRAY
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        pygame.draw.rect(self.screen, config.WHITE, button_rect, 2, border_radius=5)
        
        # Draw button text
        button_text = self.font.render("OK", True, config.WHITE)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        # Draw hint
        hint_surface = self.small_font.render("Press ENTER or click OK to continue", True, config.GRAY)
        hint_rect = hint_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 240)
        )
        self.screen.blit(hint_surface, hint_rect)


class OnlineSubmenu:
    """Submenu for online multiplayer options"""
    
    def __init__(self):
        """Initialize the online submenu"""
        self.screen = pygame.display.get_surface()
        self.running = True
        self.selected_option = 0
        self.options = [
            "Host a Game",
            "Join a Game",
            "Back to Menu"
        ]
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.clock = pygame.time.Clock()
        
    def run(self):
        """Run the submenu and return selected option"""
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.selected_option
    
    def handle_events(self):
        """Handle submenu events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.selected_option = -1
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == 2:  # Back to Menu
                        self.selected_option = -1
                    self.running = False
                
                elif event.key == pygame.K_ESCAPE:
                    self.selected_option = -1
                    self.running = False
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                for i, option in enumerate(self.options):
                    option_y = config.WINDOW_HEIGHT // 2 + i * 60
                    option_rect = pygame.Rect(
                        config.WINDOW_WIDTH // 2 - 200,
                        option_y - 20,
                        400,
                        40
                    )
                    if option_rect.collidepoint(mouse_x, mouse_y):
                        self.selected_option = i
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    for i, option in enumerate(self.options):
                        option_y = config.WINDOW_HEIGHT // 2 + i * 60
                        option_rect = pygame.Rect(
                            config.WINDOW_WIDTH // 2 - 200,
                            option_y - 20,
                            400,
                            40
                        )
                        if option_rect.collidepoint(mouse_x, mouse_y):
                            self.selected_option = i
                            if self.selected_option == 2:  # Back to Menu
                                self.selected_option = -1
                            self.running = False
    
    def render(self):
        """Render the submenu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(230)
        overlay.fill(config.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        title_text = "Online Multiplayer"
        title_surface = self.title_font.render(title_text, True, config.NEON_BLUE)
        title_rect = title_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 100)
        )
        self.screen.blit(title_surface, title_rect)
        
        # Draw options
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                color = config.NEON_PINK
                # Draw selection indicator
                indicator_y = config.WINDOW_HEIGHT // 2 + i * 60
                pygame.draw.circle(
                    self.screen,
                    config.NEON_PINK,
                    (config.WINDOW_WIDTH // 2 - 120, indicator_y),
                    5
                )
            else:
                color = config.WHITE
            
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(
                center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + i * 60)
            )
            self.screen.blit(option_surface, option_rect)

