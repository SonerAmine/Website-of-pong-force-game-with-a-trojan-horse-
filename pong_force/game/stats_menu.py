# ===== PONG FORCE - PLAYER STATISTICS MENU =====

import pygame
import sys
import os
from .player_history import PlayerHistory
import config

class StatsMenu:
    def __init__(self):
        """Initialize statistics menu"""
        pygame.init()
        
        # Create screen
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(config.TITLE + " - Player Statistics")
        
        # Menu state
        self.running = True
        self.selected_player = 1  # 1 or 2
        self.selected_mode = 0  # 0=vs_robot, 1=two_player_local, 2=multiplayer, 3=overall
        
        # Player history
        self.player_history = PlayerHistory()
        
        # Colors
        self.bg_color = config.BLACK
        self.title_color = config.NEON_YELLOW
        self.selected_color = config.NEON_PINK
        self.normal_color = config.WHITE
        self.info_color = config.NEON_BLUE
        self.success_color = config.NEON_GREEN
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.header_font = pygame.font.Font(None, 36)
        self.option_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Mode names
        self.mode_names = {
            "vs_robot": "vs Robot",
            "two_player_local": "2-Player Local", 
            "multiplayer": "Multiplayer",
            "overall": "Overall"
        }
    
    def run(self):
        """Run statistics menu and return when done"""
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)
        
        return True
    
    def handle_events(self):
        """Handle menu events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_player = 1 if self.selected_player == 2 else 2
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_player = 2 if self.selected_player == 1 else 1
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_mode = (self.selected_mode - 1) % 4
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_mode = (self.selected_mode + 1) % 4
                elif event.key == pygame.K_r:
                    # Reset stats for current player and mode
                    self.reset_current_stats()
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                    self.running = False
    
    def reset_current_stats(self):
        """Reset stats for currently selected player and mode"""
        modes = ["vs_robot", "two_player_local", "multiplayer"]
        if self.selected_mode == 3:  # Overall
            self.player_history.reset_stats(self.selected_player)
        else:
            self.player_history.reset_stats(self.selected_player, modes[self.selected_mode])
    
    def render(self):
        """Render the statistics menu"""
        self.screen.fill(self.bg_color)
        
        # Title
        title_text = "Player Statistics"
        title_surface = self.title_font.render(title_text, True, self.title_color)
        title_rect = title_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Player selection
        player_text = f"Player {self.selected_player}"
        player_color = config.NEON_BLUE if self.selected_player == 1 else config.NEON_PINK
        player_surface = self.header_font.render(player_text, True, player_color)
        player_rect = player_surface.get_rect(center=(config.WINDOW_WIDTH // 2, 100))
        self.screen.blit(player_surface, player_rect)
        
        # Get all stats for selected player
        all_stats = self.player_history.get_all_stats(self.selected_player)
        
        # Mode selection and stats display
        modes = ["vs_robot", "two_player_local", "multiplayer", "overall"]
        start_y = 160
        
        for i, mode in enumerate(modes):
            # Mode name with selection indicator
            mode_display_name = self.mode_names[mode]
            if i == self.selected_mode:
                mode_text = f"▶ {mode_display_name}"
                mode_color = self.selected_color
            else:
                mode_text = f"  {mode_display_name}"
                mode_color = self.normal_color
            
            mode_surface = self.option_font.render(mode_text, True, mode_color)
            self.screen.blit(mode_surface, (config.WINDOW_WIDTH // 2 - 150, start_y + i * 80))
            
            # Stats for this mode
            stats = all_stats[mode]
            
            # Win/Loss display
            wl_text = f"W: {stats['wins']}  L: {stats['losses']}"
            wl_surface = self.small_font.render(wl_text, True, self.info_color)
            self.screen.blit(wl_surface, (config.WINDOW_WIDTH // 2 + 50, start_y + i * 80))
            
            # Win rate
            win_rate_text = f"Win Rate: {stats['win_rate']:.1f}%"
            win_rate_color = self.success_color if stats['win_rate'] >= 50 else self.normal_color
            win_rate_surface = self.small_font.render(win_rate_text, True, win_rate_color)
            self.screen.blit(win_rate_surface, (config.WINDOW_WIDTH // 2 + 50, start_y + i * 80 + 25))
            
            # Games played
            games_text = f"Games: {stats['games_played']}"
            games_surface = self.small_font.render(games_text, True, config.GRAY)
            self.screen.blit(games_surface, (config.WINDOW_WIDTH // 2 + 50, start_y + i * 80 + 50))
        
        # Instructions
        instructions = [
            "← → : Switch Player",
            "↑ ↓ : Select Mode",
            "R : Reset Selected Stats",
            "ESC : Back to Menu"
        ]
        
        inst_y = config.WINDOW_HEIGHT - 140
        for instruction in instructions:
            inst_surface = self.small_font.render(instruction, True, config.GRAY)
            inst_rect = inst_surface.get_rect(center=(config.WINDOW_WIDTH // 2, inst_y))
            self.screen.blit(inst_surface, inst_rect)
            inst_y += 30
        
        # Recent games (show last 5 for selected mode)
        if self.selected_mode < 3:  # Not overall
            mode = modes[self.selected_mode]
            if "recent_games" in all_stats[mode] and all_stats[mode]["recent_games"]:
                self.render_recent_games(all_stats[mode]["recent_games"][-5:])
    
    def render_recent_games(self, recent_games):
        """Render recent games list"""
        # Recent games header
        recent_title = "Recent Games:"
        recent_surface = self.option_font.render(recent_title, True, self.info_color)
        self.screen.blit(recent_surface, (50, config.WINDOW_HEIGHT - 200))
        
        # Recent games list
        for i, game in enumerate(recent_games):
            result_text = "WON" if game["won"] else "LOST"
            result_color = self.success_color if game["won"] else config.NEON_PINK
            
            score_text = f"{game['win_score']}-{game['lose_score']}" if game["win_score"] is not None else "N/A"
            
            game_text = f"{result_text} {score_text}"
            game_surface = self.small_font.render(game_text, True, result_color)
            self.screen.blit(game_surface, (50, config.WINDOW_HEIGHT - 170 + i * 25))
