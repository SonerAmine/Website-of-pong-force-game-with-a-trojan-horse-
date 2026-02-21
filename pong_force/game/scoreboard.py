# ===== PONG FORCE - SCOREBOARD CLASS =====

import pygame
import config

class Scoreboard:
    def __init__(self):
        """Initialize the scoreboard"""
        self.player1_score = 0
        self.player2_score = 0
        self.win_score = config.WIN_SCORE
        self.game_over = False
        self.winner = None
        
        # Font setup
        self.large_font = pygame.font.Font(None, config.FONT_SIZE_LARGE)
        self.medium_font = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
        self.small_font = pygame.font.Font(None, config.FONT_SIZE_SMALL)
        
        # UI elements
        self.center_line = []
        self.setup_center_line()
        
        # Animation effects
        self.score_flash_duration = 0
        self.score_flash_start = 0
        self.last_score_time = 0
        
    def setup_center_line(self):
        """Setup the center line dots"""
        line_spacing = 20
        start_y = 50
        end_y = config.WINDOW_HEIGHT - 50
        
        y = start_y
        while y < end_y:
            self.center_line.append(y)
            y += line_spacing
    
    def add_score(self, player_id):
        """Add score for a player
        
        Args:
            player_id (int): Player ID (1 or 2)
        """
        if self.game_over:
            return
        
        print(f"📈 Adding score for Player {player_id}")
        print(f"   Before: P1={self.player1_score}, P2={self.player2_score}")
        
        if player_id == 1:
            self.player1_score += 1
        elif player_id == 2:
            self.player2_score += 1
        
        print(f"   After: P1={self.player1_score}, P2={self.player2_score}")
        
        # Check for win condition
        if self.player1_score >= self.win_score:
            self.game_over = True
            self.winner = 1
            print(f"🏆 Player 1 WINS! ({self.player1_score}-{self.player2_score})")
        elif self.player2_score >= self.win_score:
            self.game_over = True
            self.winner = 2
            print(f"🏆 Player 2 WINS! ({self.player1_score}-{self.player2_score})")
        
        # Flash effect
        self.score_flash_duration = 30  # frames
        self.score_flash_start = pygame.time.get_ticks()
        self.last_score_time = pygame.time.get_ticks()
    
    def reset_scores(self):
        """Reset scores to 0-0"""
        self.player1_score = 0
        self.player2_score = 0
        self.game_over = False
        self.winner = None
        self.score_flash_duration = 0
    
    def update(self, dt):
        """Update scoreboard animations
        
        Args:
            dt (float): Delta time in seconds
        """
        # Update flash effect
        if self.score_flash_duration > 0:
            self.score_flash_duration -= dt * 60
            if self.score_flash_duration <= 0:
                self.score_flash_duration = 0
    
    def draw(self, screen, ai_enabled=False, two_player_local=False, paddle1=None, paddle2=None):
        """Draw the scoreboard
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
            ai_enabled (bool): Whether AI is enabled
            two_player_local (bool): Whether 2-player local mode is enabled
            paddle1 (Paddle): Player 1 paddle object
            paddle2 (Paddle): Player 2 paddle object
        """
        # Draw center line
        self.draw_center_line(screen)
        
        # Draw scores
        self.draw_scores(screen)
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over(screen)
        
        # Draw force meters with charging indicators
        self.draw_force_meters(screen, ai_enabled, two_player_local, paddle1, paddle2)
    
    def draw_center_line(self, screen):
        """Draw the center line with dots
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        center_x = config.WINDOW_WIDTH // 2
        
        for y in self.center_line:
            pygame.draw.circle(screen, config.WHITE, (center_x, y), 3)
    
    def draw_scores(self, screen):
        """Draw player scores
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Calculate flash effect
        flash_alpha = 0
        if self.score_flash_duration > 0:
            flash_alpha = int(255 * (self.score_flash_duration / 30))
        
        # Player 1 score (left side)
        score1_text = str(self.player1_score)
        score1_surface = self.large_font.render(score1_text, True, config.NEON_BLUE)
        score1_rect = score1_surface.get_rect(center=(config.WINDOW_WIDTH // 4, 50))
        
        if flash_alpha > 0 and self.player1_score > 0:
            # Flash effect
            flash_surface = self.large_font.render(score1_text, True, config.NEON_YELLOW)
            screen.blit(flash_surface, score1_rect)
        else:
            screen.blit(score1_surface, score1_rect)
        
        # Player 2 score (right side)
        score2_text = str(self.player2_score)
        score2_surface = self.large_font.render(score2_text, True, config.NEON_PINK)
        score2_rect = score2_surface.get_rect(center=(3 * config.WINDOW_WIDTH // 4, 50))
        
        if flash_alpha > 0 and self.player2_score > 0:
            # Flash effect
            flash_surface = self.large_font.render(score2_text, True, config.NEON_YELLOW)
            screen.blit(flash_surface, score2_rect)
        else:
            screen.blit(score2_surface, score2_rect)
        
        # Draw "VS" in center
        vs_surface = self.medium_font.render("VS", True, config.WHITE)
        vs_rect = vs_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 50))
        screen.blit(vs_surface, vs_rect)
    
    def draw_game_over(self, screen):
        """Draw game over screen
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(config.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Winner text
        winner_text = f"Player {self.winner} Wins!"
        winner_surface = self.large_font.render(winner_text, True, 
                                              config.NEON_BLUE if self.winner == 1 else config.NEON_PINK)
        winner_rect = winner_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 50))
        screen.blit(winner_surface, winner_rect)
        
        # Final score
        final_score_text = f"{self.player1_score} - {self.player2_score}"
        final_score_surface = self.medium_font.render(final_score_text, True, config.WHITE)
        final_score_rect = final_score_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        screen.blit(final_score_surface, final_score_rect)
        
        # Instructions
        restart_text = "Press R to restart or DELETE to quit"
        restart_surface = self.small_font.render(restart_text, True, config.GRAY)
        restart_rect = restart_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 50))
        screen.blit(restart_surface, restart_rect)
    
    def draw_force_meters(self, screen, ai_enabled=False, two_player_local=False, paddle1=None, paddle2=None):
        """Draw force meters for both players with charging indicators
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
            ai_enabled (bool): Whether AI is enabled (hides P2 force meter)
            two_player_local (bool): Whether 2-player local mode is enabled
            paddle1 (Paddle): Player 1 paddle object
            paddle2 (Paddle): Player 2 paddle object
        """
        meter_width = config.FORCE_METER_WIDTH
        meter_height = config.FORCE_METER_HEIGHT
        meter_y = config.WINDOW_HEIGHT - config.FORCE_METER_Y_OFFSET
        
        # Player 1 force meter (left side)
        p1_meter_x = config.UI_MARGIN
        p1_rect = pygame.Rect(p1_meter_x, meter_y, meter_width, meter_height)
        pygame.draw.rect(screen, config.DARK_GRAY, p1_rect)
        pygame.draw.rect(screen, config.NEON_BLUE, p1_rect, 2)
        
        # Draw force meter indicator for Player 1
        if paddle1:
            if paddle1.force_ready:
                # Force push ready
                p1_label = self.small_font.render("Force (SPACE)", True, config.NEON_BLUE)
            else:
                # Show charging progress
                charge_text = f"Charging: {paddle1.force_meter:.0%}"
                p1_label = self.small_font.render(charge_text, True, (150, 150, 150))
        else:
            p1_label = self.small_font.render("Force (SPACE)", True, config.NEON_BLUE)
        p1_label_rect = p1_label.get_rect(center=(p1_meter_x + meter_width // 2, meter_y - 20))
        screen.blit(p1_label, p1_label_rect)
        
        # Only draw P2 force meter if NOT playing against AI OR in 2-player local mode
        if not ai_enabled or two_player_local:
            # Player 2 force meter (right side)
            p2_meter_x = config.WINDOW_WIDTH - config.UI_MARGIN - meter_width
            p2_rect = pygame.Rect(p2_meter_x, meter_y, meter_width, meter_height)
            pygame.draw.rect(screen, config.DARK_GRAY, p2_rect)
            pygame.draw.rect(screen, config.NEON_PINK, p2_rect, 2)
            
            # Draw force meter indicator for Player 2
            if paddle2:
                if paddle2.force_ready:
                    # Force push ready
                    p2_label = self.small_font.render("Force (A)" if two_player_local else "Force (E)", True, config.NEON_PINK)
                else:
                    # Show charging progress
                    charge_text = f"Charging: {paddle2.force_meter:.0%}"
                    p2_label = self.small_font.render(charge_text, True, (150, 150, 150))
            else:
                p2_label = self.small_font.render("Force (A)" if two_player_local else "Force (E)", True, config.NEON_PINK)
            p2_label_rect = p2_label.get_rect(center=(p2_meter_x + meter_width // 2, meter_y - 20))
            screen.blit(p2_label, p2_label_rect)
    
    def draw_force_meter_fill(self, screen, player_id, force_value, force_ready, cooldown_time=0):
        """Draw force meter fill for a specific player
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
            player_id (int): Player ID (1 or 2)
            force_value (float): Force value (0.0 to 1.0)
            force_ready (bool): Whether force is ready
            cooldown_time (float): Time remaining on cooldown (seconds)
        """
        meter_width = config.FORCE_METER_WIDTH
        meter_height = config.FORCE_METER_HEIGHT
        meter_y = config.WINDOW_HEIGHT - config.FORCE_METER_Y_OFFSET
        
        if player_id == 1:
            meter_x = config.UI_MARGIN
            color = config.NEON_BLUE
        else:
            meter_x = config.WINDOW_WIDTH - config.UI_MARGIN - meter_width
            color = config.NEON_PINK
        
        # Draw fill
        if force_value > 0 or cooldown_time > 0:
            # Calculate fill based on cooldown or meter value
            if cooldown_time > 0:
                fill_ratio = 1.0 - (cooldown_time / config.FORCE_COOLDOWN)
            else:
                fill_ratio = force_value
            
            fill_width = int(meter_width * fill_ratio)
            fill_rect = pygame.Rect(meter_x, meter_y, fill_width, meter_height)
            
            if force_ready:
                # Bright pulsing color when ready
                pygame.draw.rect(screen, config.NEON_YELLOW, fill_rect)
            else:
                pygame.draw.rect(screen, color, fill_rect)
        
        # Ready indicator or cooldown timer
        if force_ready:
            ready_text = "READY!"
            ready_surface = self.small_font.render(ready_text, True, config.NEON_YELLOW)
            ready_rect = ready_surface.get_rect(center=(meter_x + meter_width // 2, meter_y + meter_height + 15))
            screen.blit(ready_surface, ready_rect)
        elif cooldown_time > 0:
            # Show remaining cooldown time
            cooldown_text = f"{int(cooldown_time)}s"
            cooldown_surface = self.small_font.render(cooldown_text, True, config.GRAY)
            cooldown_rect = cooldown_surface.get_rect(center=(meter_x + meter_width // 2, meter_y + meter_height + 15))
            screen.blit(cooldown_surface, cooldown_rect)
    
    def draw_instructions(self, screen, game_state):
        """Draw game instructions
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
            game_state (str): Current game state
        """
        if game_state == config.STATE_WAITING:
            # Waiting for players
            wait_text = "Waiting for players to connect..."
            wait_surface = self.medium_font.render(wait_text, True, config.WHITE)
            wait_rect = wait_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
            screen.blit(wait_surface, wait_rect)
            
        elif game_state == config.STATE_PLAYING:
            # Game controls
            controls = [
                "Player 1: Arrow Keys | Player 2: W/S",
                "Force Push: SPACE (P1) | SHIFT (P2)",
                "Pause: ESC | Restart: R"
            ]
            
            for i, control in enumerate(controls):
                control_surface = self.small_font.render(control, True, config.GRAY)
                control_rect = control_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 
                                                              config.WINDOW_HEIGHT - 100 + i * 20))
                screen.blit(control_surface, control_rect)
        
        elif game_state == config.STATE_PAUSED:
            # Paused
            pause_text = "PAUSED - Press ESC to resume"
            pause_surface = self.medium_font.render(pause_text, True, config.NEON_YELLOW)
            pause_rect = pause_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
            screen.blit(pause_surface, pause_rect)
    
    def get_state(self):
        """Get scoreboard state for networking
        
        Returns:
            dict: Scoreboard state data
        """
        return {
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'game_over': self.game_over,
            'winner': self.winner
        }
    
    def set_state(self, state):
        """Set scoreboard state from network data
        
        Args:
            state (dict): Scoreboard state data
        """
        self.player1_score = state['player1_score']
        self.player2_score = state['player2_score']
        self.game_over = state['game_over']
        self.winner = state['winner']
