# ===== PONG FORCE - MAIN GAME LOOP =====



import pygame

import sys

import time

from .paddle import Paddle

from .ball import Ball

from .power import ForcePush

from .scoreboard import Scoreboard

from .effects import EffectsManager

from .player_history import PlayerHistory

import config



class GameLoop:

    def __init__(self, fullscreen=False):

        """Initialize the game loop

        

        Args:

            fullscreen (bool): Start in fullscreen mode

        """

        # Pygame should already be initialized by main.py

        # Just ensure it's initialized

        if not pygame.get_init():

            pygame.init()

        if not pygame.mixer.get_init():

            pygame.mixer.init()

        

        # Screen settings

        self.fullscreen = fullscreen

        self.windowed_size = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        

        # Always use existing display surface (menu created it)

        # Just update the caption

        self.screen = pygame.display.get_surface()

        if self.screen is None:

            # Create new surface only if none exists

            if self.fullscreen:

                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

            else:

                # Use RESIZABLE flag to enable window buttons (minimize, maximize, close)

                self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

        

        pygame.display.set_caption(config.TITLE + " - Game")

        

        # Game clock

        self.clock = pygame.time.Clock()

        self.running = True

        self.game_state = config.STATE_PLAYING

        

        # Game objects

        self.paddle1 = Paddle(

            config.PADDLE_MARGIN, 

            config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2,

            1, 

            config.NEON_BLUE

        )

        

        self.paddle2 = Paddle(

            config.WINDOW_WIDTH - config.PADDLE_MARGIN - config.PADDLE_WIDTH,

            config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2,

            2,

            config.NEON_PINK

        )

        

        self.ball = Ball(

            config.WINDOW_WIDTH // 2 - config.BALL_SIZE // 2,

            config.WINDOW_HEIGHT // 2 - config.BALL_SIZE // 2

        )

        

        self.force_push = ForcePush()

        self.scoreboard = Scoreboard()

        self.effects = EffectsManager()

        

        # Input handling

        self.keys_pressed = set()

        self.keys_just_pressed = set()

        

        # Performance tracking

        self.fps_counter = 0

        self.fps_timer = 0

        self.current_fps = 0

        

        # Network state (for multiplayer)

        self.is_server = False

        self.is_client = False

        self.network_connected = False

        

        # AI state

        self.ai_enabled = False

        self.two_player_local = False  # New mode

        self.ai_difficulty = 0.50  # 0.0 to 1.0 (higher = smarter AI) - Réduit à 0.50 pour être plus facile

        self.custom_win_score = config.WIN_SCORE  # Custom win score for matches

        

        # Custom controls system

        self.controls_menu = None

        self.custom_controls = {

            "player1": {"multiplayer": {"up": "up", "down": "down", "force": "space"},

                         "vs_robot": {"up": "up", "down": "down", "force": "space"},

                         "two_player_local": {"up": "up", "down": "down", "force": "space"}},

            "player2": {"multiplayer": {"up": "w", "down": "s", "force": "shift"},

                         "vs_robot": {"up": "w", "down": "s", "force": "shift"},

                         "two_player_local": {"up": "z", "down": "s", "force": "a"}}

        }

        

        # Score delay timer (non-blocking)

        self.score_delay_active = False

        self.score_delay_timer = 0

        self.score_delay_duration = 1.5  # seconds

        

        # Player history system
        self.player_history = PlayerHistory()

        

    def run_local(self):

        """Run local multiplayer game"""

        print("🎮 Starting local multiplayer game...")

        self.is_server = True

        self.game_state = config.STATE_PLAYING

        self.main_loop()

    

    def run_vs_ai(self):

        """Run game against AI"""

        print("🤖 Starting game vs AI...")

        self.ai_enabled = True

        self.load_custom_controls()

        self.game_state = config.STATE_PLAYING

        self.main_loop()

    

    def run_vs_ai_with_goals(self, win_score):

        """Run game against AI with custom win score"""

        print("Starting game vs AI - First to {win_score} wins!")

        self.ai_enabled = True

        self.custom_win_score = win_score

        self.load_custom_controls()

        self.game_state = config.STATE_PLAYING

        self.main_loop()

    

    def load_custom_controls(self):

        """Load custom controls from file"""

        try:

            import json
            import os

            controls_file = os.path.join(os.path.dirname(__file__), "..", "controls.json")
            if os.path.exists(controls_file):

                with open(controls_file, 'r') as f:

                    self.custom_controls = json.load(f)

                    print("Custom controls loaded")

        except Exception as e:

            print(f"Error loading custom controls: {e}")

    

    def get_control_key(self, player, action):

        """Get pygame key for player action based on game mode"""

        if self.ai_enabled:

            mode = "vs_robot"

        elif self.two_player_local:

            mode = "two_player_local"

        else:

            mode = "multiplayer"

        

        control_name = self.custom_controls[f"player{player}"][mode][action]

        

        # Convert control name to pygame key

        key_map = {

            "up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT,

            "space": pygame.K_SPACE, "shift": pygame.K_LSHIFT,

            "w": pygame.K_w, "a": pygame.K_a, "s": pygame.K_s, "d": pygame.K_d,

            "z": pygame.K_z, "x": pygame.K_x, "c": pygame.K_c, "v": pygame.K_v,

            "q": pygame.K_q, "e": pygame.K_e, "r": pygame.K_r, "f": pygame.K_f,

            "g": pygame.K_g, "h": pygame.K_h, "y": pygame.K_y, "u": pygame.K_u,

            "i": pygame.K_i, "j": pygame.K_j, "k": pygame.K_k, "l": pygame.K_l,

            "m": pygame.K_m, "n": pygame.K_n, "b": pygame.K_b, "o": pygame.K_o,

            "p": pygame.K_p

        }

        return key_map.get(control_name, pygame.K_UP)  # Default to UP if not found

    

    def run_two_player_local(self, win_score):

        """Run 2-player local game with custom win score"""

        print(f"Starting 2-player local game - First to {win_score} wins!")

        self.two_player_local = True

        self.custom_win_score = win_score

        self.load_custom_controls()

        self.game_state = config.STATE_PLAYING

        self.main_loop()

    

    def run_server(self):

        """Run as server"""

        print("🎮 Starting server game...")

        self.is_server = True

        self.game_state = config.STATE_WAITING

        self.main_loop()

    

    def run_client(self):

        """Run as client"""

        print("🎮 Starting client game...")

        self.is_client = True

        self.game_state = config.STATE_CONNECTING

        self.main_loop()

    

    def main_loop(self):

        """Main game loop"""

        last_time = time.time()

        

        while self.running:

            current_time = time.time()

            dt = current_time - last_time

            last_time = current_time

            

            # Handle events

            self.handle_events()

            

            # Update game state

            self.update(dt)

            # Broadcast game state to clients if server (at network update rate)
            if self.is_server and hasattr(self, 'server'):
                # Broadcast at network update rate (60 times per second)
                if not hasattr(self, '_last_broadcast_time'):
                    self._last_broadcast_time = current_time
                    self._broadcast_interval = 1.0 / config.NETWORK_UPDATE_RATE
                
                if current_time - self._last_broadcast_time >= self._broadcast_interval:
                    self.server.broadcast_game_state()
                    # Note: relay inputs are polled in a separate thread (relay_polling_loop)
                    self._last_broadcast_time = current_time

            # Render

            self.render()

            

            # Update display

            pygame.display.flip()

            

            # Cap frame rate

            self.clock.tick(config.FPS)

            

            # Update FPS counter

            self.update_fps_counter(dt)

    

    def handle_events(self):

        """Handle pygame events"""

        self.keys_just_pressed.clear()

        

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            

            elif event.type == pygame.VIDEORESIZE:

                # Handle window resize

                self.windowed_size = (event.w, event.h)

                if not self.fullscreen:

                    self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

            

            elif event.type == pygame.KEYDOWN:

                self.keys_just_pressed.add(event.key)

                self.keys_pressed.add(event.key)

                

                # Handle key presses

                self.handle_key_press(event.key)

            

            elif event.type == pygame.KEYUP:

                self.keys_pressed.discard(event.key)

    

    def handle_key_press(self, key):

        """Handle individual key presses

        

        Args:

            key (int): Pygame key constant

        """

        if key == pygame.K_ESCAPE:

            if self.game_state == config.STATE_PLAYING:

                self.game_state = config.STATE_PAUSED

            elif self.game_state == config.STATE_PAUSED:

                self.game_state = config.STATE_PLAYING

            elif self.game_state == config.STATE_GAME_OVER:

                self.running = False  # Return to menu

        

        elif key == pygame.K_q:

            # Return to menu (don't quit completely)

            self.running = False

        

        elif key == pygame.K_F11 or key == pygame.K_f:

            # Toggle fullscreen

            self.toggle_fullscreen()

        

        elif key == pygame.K_r:

            if self.game_state == config.STATE_GAME_OVER:

                self.restart_game()

        

        elif key == pygame.K_SPACE:

            print(f"🎮 TOUCHE ESPACE PRESSÉE ! game_state={self.game_state}, score_delay={self.score_delay_active}")

            if self.game_state == config.STATE_PLAYING and not self.score_delay_active:

                print("   État OK - Appel de try_force_push")

                # Player 1 force push - use custom control

                result = self.paddle1.try_force_push(self.ball)

                print(f"   Résultat try_force_push: {result}")

                if result:

                    self.effects.create_force_effect(

                        self.ball.x + self.ball.size // 2,

                        self.ball.y + self.ball.size // 2,

                        1

                    )

                    print("   Effet visuel cree")

            else:

                print(f"   Etat pas OK pour Force Push")

        

        # Check for custom force push keys

        p1_force_key = self.get_control_key(1, "force")

        p2_force_key = self.get_control_key(2, "force") if not self.ai_enabled else None

        

        if key == p1_force_key:

            if self.game_state == config.STATE_PLAYING and not self.score_delay_active:

                result = self.paddle1.try_force_push(self.ball)

                if result:

                    self.effects.create_force_effect(

                        self.ball.x + self.ball.size // 2,

                        self.ball.y + self.ball.size // 2,

                        1

                    )

        

        elif key == p2_force_key:

            if self.game_state == config.STATE_PLAYING and not self.score_delay_active:

                # Player 2 force push (only if not AI)

                if not self.ai_enabled and self.paddle2.try_force_push(self.ball):

                    self.effects.create_force_effect(

                        self.ball.x + self.ball.size // 2,

                        self.ball.y + self.ball.size // 2,

                        2

                    )

    

    def update(self, dt):

        """Update game state

        

        Args:

            dt (float): Delta time in seconds

        """

        # Update score delay timer

        if self.score_delay_active:

            self.score_delay_timer += dt

            if self.score_delay_timer >= self.score_delay_duration:

                self.score_delay_active = False

                self.score_delay_timer = 0

                self.ball.reset_ball()

        

        # Update input (only for host/server, not for client)
        # Client receives game state from server, so it doesn't process input locally

        if not self.score_delay_active and not self.is_client:

            self.update_input()

        

        # Update game objects
        # Client receives state from server, so it doesn't simulate gameplay
        # Only server/host simulates the game

        if self.game_state == config.STATE_PLAYING and not self.score_delay_active and not self.is_client:

            self.update_gameplay(dt)

        

        # Update effects (always update, even for client)

        self.effects.update(dt)

        self.force_push.update(dt)

        

        # Update paddles visually (for effects like glow, trail) even if client
        # Position comes from server, but visual effects need updating
        if self.game_state == config.STATE_PLAYING and self.is_client:
            # Client: only update visual effects, not movement (position comes from server)
            # Update visual effects without modifying position
            self.paddle1.update_visual_effects(dt)
            self.paddle2.update_visual_effects(dt)
            # Update collision rectangles for rendering
            self.paddle1.rect.x = self.paddle1.x
            self.paddle1.rect.y = self.paddle1.y
            self.paddle2.rect.x = self.paddle2.x
            self.paddle2.rect.y = self.paddle2.y

        # Update scoreboard

        self.scoreboard.update(dt)

        

        # Check game over from scoreboard

        if self.scoreboard.game_over and self.game_state == config.STATE_PLAYING:

            self.game_state = config.STATE_GAME_OVER

            print("🏆 Game Over!")

    

    def update_input(self):

        """Update input handling with custom controls"""

        # Player 1 controls (customizable) - Host controls paddle1

        p1_up_key = self.get_control_key(1, "up")

        p1_down_key = self.get_control_key(1, "down")

        p1_force_key = self.get_control_key(1, "force")

        

        if p1_up_key in self.keys_pressed:

            self.paddle1.move_up()

        elif p1_down_key in self.keys_pressed:

            self.paddle1.move_down()

        else:

            self.paddle1.stop_moving()

        

        # Player 2 controls (depends on mode)

        if self.is_server:

            # In server mode, player 2 is controlled by client via network

            # Don't process keyboard input for paddle2 - it's controlled by network

            pass

        elif self.ai_enabled:

            # AI controls player 2

            self.update_ai()

        else:

            # Human player 2 controls (customizable) - for local 2-player or client mode

            p2_up_key = self.get_control_key(2, "up")

            p2_down_key = self.get_control_key(2, "down")

            p2_force_key = self.get_control_key(2, "force")

            

            if p2_up_key in self.keys_pressed:

                self.paddle2.move_up()

            elif p2_down_key in self.keys_pressed:

                self.paddle2.move_down()

            else:

                self.paddle2.stop_moving()

    

    def update_gameplay(self, dt):

        """Update gameplay logic

        

        Args:

            dt (float): Delta time in seconds

        """

        # Update paddles

        self.paddle1.update(dt, config.WINDOW_HEIGHT)

        self.paddle2.update(dt, config.WINDOW_HEIGHT)

        

        # Update ball

        result = self.ball.update(dt, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        

        # Handle ball scoring when it goes off screen

        if result == "score_left":

            # Ball went off left side - Player 2 (right) scores

            print("⚽ Ball went off LEFT side!")

            self.handle_score(2)  # Player 2 scores

            return  # Don't continue updating this frame

        elif result == "score_right":

            # Ball went off right side - Player 1 (left) scores

            print("⚽ Ball went off RIGHT side!")

            self.handle_score(1)  # Player 1 scores

            return  # Don't continue updating this frame

        

        # Check paddle collisions

        if self.ball.collide_with_paddle(self.paddle1):

            self.effects.create_hit_effect(

                self.ball.x + self.ball.size // 2,

                self.ball.y + self.ball.size // 2,

                config.NEON_BLUE

            )

        

        if self.ball.collide_with_paddle(self.paddle2):

            self.effects.create_hit_effect(

                self.ball.x + self.ball.size // 2,

                self.ball.y + self.ball.size // 2,

                config.NEON_PINK

            )

    

    def handle_score(self, player_id):

        """Handle scoring

        

        Args:

            player_id (int): Player who scored

        """

        print(f"🎯 GOAL! Player {player_id} scored!")

        

        # Add score immediately

        self.scoreboard.add_score(player_id)

        print(f"📊 Score: {self.scoreboard.player1_score} - {self.scoreboard.player2_score}")

        

        # Create score effect

        self.effects.create_score_effect(player_id)

        

        # Reset ball position to center immediately

        self.ball.x = config.WINDOW_WIDTH // 2 - self.ball.size // 2

        self.ball.y = config.WINDOW_HEIGHT // 2 - self.ball.size // 2

        

        # Reset ball speed to initial when someone scores

        self.ball.reset_ball()

        

        # Start non-blocking delay before ball moves again

        self.score_delay_active = True

        self.score_delay_timer = 0

        

        # Stop ball movement during delay (already done by reset_ball)

        self.ball.vx = 0

        self.ball.vy = 0

        

        # Check for game over with custom win score

        if self.scoreboard.player1_score >= self.custom_win_score or self.scoreboard.player2_score >= self.custom_win_score:

            print(f"🏆 GAME OVER! Final Score: {self.scoreboard.player1_score} - {self.scoreboard.player2_score}")

            self.scoreboard.game_over = True

            self.game_state = config.STATE_GAME_OVER

            

            # Record game results in player history
            self.record_game_result()

    

    def record_game_result(self):
        """Record the game result in player history"""
        # Determine game mode
        if self.ai_enabled:
            mode = "vs_robot"
        elif self.two_player_local:
            mode = "two_player_local"
        else:
            mode = "multiplayer"
        
        # Determine winner and record results
        if self.scoreboard.player1_score >= self.custom_win_score:
            # Player 1 won
            self.player_history.record_game(
                1, mode, True, 
                self.scoreboard.player1_score, 
                self.scoreboard.player2_score
            )
            
            # Player 2 lost (only in 2-player local mode)
            if self.two_player_local:
                self.player_history.record_game(
                    2, mode, False,
                    self.scoreboard.player2_score,
                    self.scoreboard.player1_score
                )
                
        elif self.scoreboard.player2_score >= self.custom_win_score:
            # Player 2 won (only record if in 2-player local mode)
            if self.two_player_local:
                self.player_history.record_game(
                    2, mode, True,
                    self.scoreboard.player2_score,
                    self.scoreboard.player1_score
                )
            
            # Player 1 lost
            self.player_history.record_game(
                1, mode, False,
                self.scoreboard.player1_score,
                self.scoreboard.player2_score
            )
        
        print(f"📈 Game result recorded for mode: {mode}")

    

    def restart_game(self):

        """Restart the game"""

        self.scoreboard.reset_scores()

        self.ball.reset_ball()

        self.paddle1.y = config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2

        self.paddle2.y = config.WINDOW_HEIGHT // 2 - config.PADDLE_HEIGHT // 2

        

        # Reset force meters for both players

        self.paddle1.force_meter = 0.0

        self.paddle1.force_ready = False

        self.paddle1.force_cooldown = 0.0

        self.paddle2.force_meter = 0.0

        self.paddle2.force_ready = False

        self.paddle2.force_cooldown = 0.0

        

        self.effects.clear_effects()

        self.force_push.clear_effects()

        self.game_state = config.STATE_PLAYING

    

    def update_fps_counter(self, dt):

        """Update FPS counter

        

        Args:

            dt (float): Delta time in seconds

        """

        self.fps_counter += 1

        self.fps_timer += dt

        

        if self.fps_timer >= 1.0:  # Update every second

            self.current_fps = self.fps_counter

            self.fps_counter = 0

            self.fps_timer = 0

    

    def render(self):

        """Render the game"""

        # Clear screen

        self.screen.fill(config.BLACK)

        

        # Apply screen shake

        shake_offset = self.effects.get_screen_shake()

        if shake_offset != (0, 0):

            # Create a temporary surface for shake effect

            temp_surface = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

            temp_surface.fill(config.BLACK)

            self.render_to_surface(temp_surface)

            self.screen.blit(temp_surface, shake_offset)

        else:

            self.render_to_surface(self.screen)

        

        # Draw FPS counter

        if config.SHOW_FPS:

            self.draw_fps_counter()

    

    def render_to_surface(self, surface):

        """Render game to a specific surface

        

        Args:

            surface (pygame.Surface): Surface to render to

        """

        # Draw background effects

        self.effects.draw(surface)

        

        # Draw game objects

        if self.game_state in [config.STATE_PLAYING, config.STATE_PAUSED, config.STATE_GAME_OVER]:

            self.paddle1.draw(surface)

            self.paddle2.draw(surface)

            self.ball.draw(surface)

            self.force_push.draw(surface)

        

        # Draw UI (pass AI status and paddle objects for force meter indicators)

        self.scoreboard.draw(surface, self.ai_enabled, self.two_player_local, self.paddle1, self.paddle2)

        

        # Draw force meter fills for paddles

        if self.game_state in [config.STATE_PLAYING, config.STATE_PAUSED]:

            self.scoreboard.draw_force_meter_fill(surface, 1, self.paddle1.force_meter, 

                                                  self.paddle1.force_ready, self.paddle1.force_cooldown)

            if not self.ai_enabled:  # Only draw P2 meter if not against AI

                self.scoreboard.draw_force_meter_fill(surface, 2, self.paddle2.force_meter, 

                                                      self.paddle2.force_ready, self.paddle2.force_cooldown)

            # Always show P2 meter in 2-player local mode

            elif self.two_player_local:

                self.scoreboard.draw_force_meter_fill(surface, 2, self.paddle2.force_meter, 

                                                      self.paddle2.force_ready, self.paddle2.force_cooldown)

        

        # Draw quit button (always visible during gameplay)

        if self.game_state in [config.STATE_PLAYING, config.STATE_PAUSED]:

            self.draw_quit_button(surface)

        

        # Draw game state specific UI

        if self.game_state == config.STATE_PAUSED:

            self.draw_pause_screen(surface)

        elif self.game_state == config.STATE_GAME_OVER:

            self.draw_game_over_screen(surface)

        elif self.game_state == config.STATE_WAITING:

            self.draw_waiting_screen(surface)

        elif self.game_state == config.STATE_CONNECTING:

            self.draw_connecting_screen(surface)

    

    def draw_fps_counter(self):

        """Draw FPS counter"""

        font = pygame.font.Font(None, 24)

        fps_text = f"FPS: {self.current_fps}"

        fps_surface = font.render(fps_text, True, config.WHITE)

        self.screen.blit(fps_surface, (10, 10))

    

    def draw_quit_button(self, surface):

        """Draw quit button in top-right corner"""

        # Button dimensions

        button_width = 120

        button_height = 35

        button_x = config.WINDOW_WIDTH - button_width - 10

        button_y = 10

        

        # Draw button background

        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        

        # Check if mouse is over button

        mouse_pos = pygame.mouse.get_pos()

        is_hover = button_rect.collidepoint(mouse_pos)

        

        # Button color based on hover

        if is_hover:

            button_color = config.NEON_PINK

            text_color = config.NEON_YELLOW

        else:

            button_color = config.DARK_GRAY

            text_color = config.WHITE

        

        # Draw button

        pygame.draw.rect(surface, button_color, button_rect, border_radius=5)

        pygame.draw.rect(surface, config.WHITE, button_rect, 2, border_radius=5)

        

        # Draw button text

        font = pygame.font.Font(None, 22)

        text_surface = font.render("Menu (Q)", True, text_color)

        text_rect = text_surface.get_rect(center=button_rect.center)

        surface.blit(text_surface, text_rect)

        

        # Handle click - return to menu instead of quitting

        mouse_buttons = pygame.mouse.get_pressed()

        if is_hover and mouse_buttons[0]:  # Left click

            self.running = False  # Return to menu

    

    def draw_pause_screen(self, surface):

        """Draw pause screen overlay

        

        Args:

            surface (pygame.Surface): Surface to draw on

        """

        # Semi-transparent overlay

        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        overlay.set_alpha(200)

        overlay.fill(config.BLACK)

        surface.blit(overlay, (0, 0))

        

        # Pause text

        font = pygame.font.Font(None, 72)

        pause_text = "PAUSED"

        pause_surface = font.render(pause_text, True, config.NEON_YELLOW)

        pause_rect = pause_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 60))

        surface.blit(pause_surface, pause_rect)

        

        # Instructions

        font_small = pygame.font.Font(None, 28)

        instructions = [

            "Press ESC to resume",

            "Press Q to quit game",

            "Press F11 for fullscreen",

            "",

            "Controls:",

            "P1: Arrows + SPACE",

            "P2: W/S + E",

            "",

            f"First to {config.WIN_SCORE} wins!"

        ]

        

        y_offset = config.WINDOW_HEIGHT // 2 + 20

        for instruction in instructions:

            instruction_surface = font_small.render(instruction, True, config.WHITE)

            instruction_rect = instruction_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))

            surface.blit(instruction_surface, instruction_rect)

            y_offset += 40

    

    def draw_game_over_screen(self, surface):

        """Draw game over screen with quit option

        

        Args:

            surface (pygame.Surface): Surface to draw on

        """

        # Draw scoreboard's game over first

        # Then add quit instruction

        font_small = pygame.font.Font(None, 24)

        quit_text = "Press ESC to return to menu"

        quit_surface = font_small.render(quit_text, True, config.GRAY)

        quit_rect = quit_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 100))

        surface.blit(quit_surface, quit_rect)

    

    def draw_waiting_screen(self, surface):
        """Draw waiting for players screen with animation

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        import math

        # Animated title
        font = pygame.font.Font(None, 48)
        wait_text = "Waiting for Players"

        # Pulsing effect
        pulse = 0.8 + 0.2 * math.sin(time.time() * 3)
        color = (
            int(config.NEON_BLUE[0] * pulse),
            int(config.NEON_BLUE[1] * pulse),
            int(config.NEON_BLUE[2] * pulse)
        )

        wait_surface = font.render(wait_text, True, color)
        wait_rect = wait_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 40))
        surface.blit(wait_surface, wait_rect)

        # Animated dots
        dots_count = int((time.time() * 2) % 4)
        dots_text = "." * dots_count
        dots_surface = font.render(dots_text, True, color)
        dots_rect = dots_surface.get_rect(
            topleft=(wait_rect.right + 5, wait_rect.top)
        )
        surface.blit(dots_surface, dots_rect)

        # Press ESC to cancel hint
        font_small = pygame.font.Font(None, 24)
        hint_surface = font_small.render("Press ESC or Q to return to menu", True, config.GRAY)
        hint_rect = hint_surface.get_rect(
            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 30)
        )
        surface.blit(hint_surface, hint_rect)

    

    def draw_connecting_screen(self, surface):

        """Draw connecting screen with animation

        

        Args:

            surface (pygame.Surface): Surface to draw on

        """

        import math

        

        # Animated title

        font = pygame.font.Font(None, 48)

        connect_text = "Connecting to Server"

        

        # Pulsing effect

        pulse = 0.7 + 0.3 * math.sin(time.time() * 4)

        color = (

            int(config.NEON_PINK[0] * pulse),

            int(config.NEON_PINK[1] * pulse),

            int(config.NEON_PINK[2] * pulse)

        )

        

        connect_surface = font.render(connect_text, True, color)

        connect_rect = connect_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 80))

        surface.blit(connect_surface, connect_rect)

        

        # Animated loading dots

        dots_count = int((time.time() * 3) % 4)

        dots_text = "." * dots_count

        dots_surface = font.render(dots_text, True, color)

        dots_rect = dots_surface.get_rect(

            topleft=(connect_rect.right + 5, connect_rect.top)

        )

        surface.blit(dots_surface, dots_rect)

        

        # Spinner animation

        spinner_radius = 40

        spinner_thickness = 6

        spinner_center = (config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 20)

        

        # Draw spinner circle

        num_segments = 12

        for i in range(num_segments):

            angle = (time.time() * 5 + i * (360 / num_segments)) % 360

            angle_rad = math.radians(angle)

            

            # Calculate segment position

            x = spinner_center[0] + math.cos(angle_rad) * spinner_radius

            y = spinner_center[1] + math.sin(angle_rad) * spinner_radius

            

            # Fade segments based on position

            alpha = int(255 * (1 - i / num_segments))

            segment_color = (

                int(config.NEON_BLUE[0] * alpha / 255),

                int(config.NEON_BLUE[1] * alpha / 255),

                int(config.NEON_BLUE[2] * alpha / 255)

            )

            

            pygame.draw.circle(surface, segment_color, (int(x), int(y)), spinner_thickness)

        

        # Connection info

        font_small = pygame.font.Font(None, 24)

        

        info_lines = [

            "Please wait while establishing connection...",

            "",

            "This may take up to 10 seconds",

            "",

            "If connection fails, please check:",

            "• Server is running",

            "• IP address is correct",

            "• Port is correct (default: 5555)",

            "• Firewall allows connection"

        ]

        

        y_offset = config.WINDOW_HEIGHT // 2 + 100

        for line in info_lines:

            if line:

                text_surface = font_small.render(line, True, config.WHITE)

                text_rect = text_surface.get_rect(center=(config.WINDOW_WIDTH // 2, y_offset))

                surface.blit(text_surface, text_rect)

            y_offset += 25

        

        # Cancel hint

        hint_surface = font_small.render("Press ESC to cancel", True, config.GRAY)

        hint_rect = hint_surface.get_rect(

            center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 30)

        )

        surface.blit(hint_surface, hint_rect)

    

    def toggle_fullscreen(self):

        """Toggle between fullscreen and windowed mode"""

        self.fullscreen = not self.fullscreen

        

        if self.fullscreen:

            # Get current display info for fullscreen

            display_info = pygame.display.Info()

            self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)

        else:

            # Return to windowed mode with RESIZABLE flag

            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

        

        print(f"{'🖥️ Fullscreen' if self.fullscreen else '🪟 Windowed'} mode")

    

    def update_ai(self):

        """Update AI paddle movement with improved intelligence"""

        if not self.ai_enabled or self.score_delay_active:

            return

        

        import random

        import math

        

        # AI controls paddle 2

        paddle_center_y = self.paddle2.y + self.paddle2.height // 2

        ball_center_y = self.ball.y + self.ball.size // 2

        ball_center_x = self.ball.x + self.ball.size // 2

        

        # Predict where the ball will be

        if self.ball.vx > 0:  # Ball moving towards AI

            # Calculate intersection point

            time_to_reach = (self.paddle2.x - ball_center_x) / max(abs(self.ball.vx), 0.1)

            predicted_y = ball_center_y + (self.ball.vy * time_to_reach)

            

            # Account for wall bounces

            while predicted_y < 0 or predicted_y > config.WINDOW_HEIGHT:

                if predicted_y < 0:

                    predicted_y = abs(predicted_y)

                elif predicted_y > config.WINDOW_HEIGHT:

                    predicted_y = 2 * config.WINDOW_HEIGHT - predicted_y

            

            # Add difficulty-based error (augmenté pour rendre l'IA plus facile)

            prediction_error = (1 - self.ai_difficulty) * 120  # Augmenté de 50 à 120

            target_y = predicted_y + random.uniform(-prediction_error, prediction_error)

        else:

            # Ball moving away - return to center

            target_y = config.WINDOW_HEIGHT // 2

        

        # Move paddle towards target position

        threshold = 30  # Dead zone augmentée (était 10) pour que l'IA soit moins réactive

        speed_multiplier = 0.6  # Réduire la vitesse de l'IA

        

        if target_y < paddle_center_y - threshold:

            self.paddle2.move_up()

            # Ralentir l'IA

            self.paddle2.y -= self.paddle2.speed * 0.05  # Très ralenti

        elif target_y > paddle_center_y + threshold:

            self.paddle2.move_down()

            # Ralentir l'IA

            self.paddle2.y += self.paddle2.speed * 0.05  # Très ralenti

        else:

            self.paddle2.stop_moving()

        

        # AI Force Push Logic

        # AI can use force push when meter is full and ball is close

        if self.paddle2.force_ready and self.ball.vx > 0:  # Ball moving towards AI

            # Calculate distance to ball

            ball_center_x = self.ball.x + self.ball.size // 2

            ball_center_y = self.ball.y + self.ball.size // 2

            paddle_center_y = self.paddle2.y + self.paddle2.height // 2

            

            # Check if ball is in range for force push

            distance = abs(ball_center_x - self.paddle2.x)

            y_distance = abs(ball_center_y - paddle_center_y)

            

            # AI uses force push when ball is close and moving fast

            if (distance < 150 and y_distance < 100 and 

                abs(self.ball.vx) > 8 and 

                random.random() < self.ai_difficulty * 0.7):  # Probability based on difficulty

                

                if self.paddle2.try_force_push(self.ball):

                    print(f"🤖 AI used Force Push!")

                    # Create visual effect for AI force push

                    self.effects.create_force_effect(

                        self.ball.x + self.ball.size // 2,

                        self.ball.y + self.ball.size // 2,

                        config.NEON_PINK

                    )

        pass

    

    def cleanup(self):

        """Cleanup resources"""

        pygame.quit()

    

    def get_game_state(self):

        """Get current game state for networking

        

        Returns:

            dict: Game state data

        """

        return {

            'game_state': self.game_state,

            'paddle1': self.paddle1.get_state(),

            'paddle2': self.paddle2.get_state(),

            'ball': self.ball.get_state(),

            'scoreboard': self.scoreboard.get_state()

        }

    

    def set_game_state(self, state):

        """Set game state from network data

        

        Args:

            state (dict): Game state data

        """

        self.game_state = state['game_state']

        self.paddle1.set_state(state['paddle1'])

        self.paddle2.set_state(state['paddle2'])

        self.ball.set_state(state['ball'])

        self.scoreboard.set_state(state['scoreboard'])

