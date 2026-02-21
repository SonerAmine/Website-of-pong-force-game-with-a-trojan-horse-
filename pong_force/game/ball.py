# ===== PONG FORCE - BALL CLASS =====

import pygame
import math
import random
import config

class Ball:
    def __init__(self, x, y):
        """Initialize the ball
        
        Args:
            x (int): Initial X position
            y (int): Initial Y position
        """
        self.x = x
        self.y = y
        self.size = config.BALL_SIZE
        self.base_speed = config.BALL_SPEED
        self.speed = self.base_speed
        
        # Speed tracking for logical gameplay
        self.speed_multiplier = 1.0
        self.hit_count = 0
        
        # Movement
        self.vx = 0
        self.vy = 0
        self.angle = 0
        
        # Force push effects
        self.force_active = False
        self.force_end_time = 0
        self.force_multiplier = 1.0
        self.force_player = 0
        
        # Visual effects
        self.trail = []
        self.max_trail_length = config.BALL_TRAIL_LENGTH
        self.glow_intensity = 0.0
        self.target_glow = 0.0
        
        # Screen shake effect
        self.shake_intensity = 0
        self.shake_duration = 0
        
        # Create rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        # Initialize with random direction
        self.reset_ball()
    
    def reset_ball(self, direction=None):
        """Reset ball to center with random direction
        
        Args:
            direction (int): Direction to go (1 for right, -1 for left, None for random)
        """
        self.x = config.WINDOW_WIDTH // 2 - self.size // 2
        self.y = config.WINDOW_HEIGHT // 2 - self.size // 2
        
        # Random angle between -45 and 45 degrees
        if direction is None:
            direction = random.choice([-1, 1])
        
        angle_degrees = random.uniform(-45, 45)
        self.angle = math.radians(angle_degrees)
        
        # Reset speed to initial when scoring
        self.speed = self.base_speed
        self.speed_multiplier = 1.0
        self.hit_count = 0
        
        # Set velocity based on angle and direction
        self.vx = direction * self.speed * math.cos(self.angle)
        self.vy = self.speed * math.sin(self.angle)
        
        # Reset effects
        self.force_active = False
        self.force_multiplier = 1.0
        self.force_player = 0
        self.target_glow = 0.0
        self.trail = []
        
        # Update collision rectangle
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update(self, dt, screen_width, screen_height):
        """Update ball position and effects
        
        Args:
            dt (float): Delta time in seconds
            screen_width (int): Screen width for boundary checking
            screen_height (int): Screen height for boundary checking
        
        Returns:
            str or None: "score_left" or "score_right" if ball went off screen, None otherwise
        """
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Update force push effect
        self.update_force_effect(current_time)
        
        # Update movement and get scoring result
        result = self.update_movement(dt, screen_width, screen_height)
        
        # Update visual effects
        self.update_visual_effects(dt)
        
        # Update collision rectangle
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Return scoring result
        return result
    
    def update_force_effect(self, current_time):
        """Update force push effect"""
        if self.force_active and current_time >= self.force_end_time:
            self.force_active = False
            self.force_multiplier = 1.0
            self.target_glow = 0.0
        elif self.force_active:
            # Fade out force effect
            time_left = self.force_end_time - current_time
            fade_ratio = time_left / config.FORCE_EFFECT_DURATION
            self.force_multiplier = 1.0 + (config.FORCE_MULTIPLIER - 1.0) * fade_ratio
            self.target_glow = fade_ratio
    
    def update_movement(self, dt, screen_width, screen_height):
        """Update ball movement and collision detection"""
        # Add to trail
        self.trail.append((self.x + self.size // 2, self.y + self.size // 2))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Apply velocity with force multiplier
        current_speed = self.speed * self.force_multiplier
        self.x += self.vx * dt * 60  # Normalize for 60 FPS
        self.y += self.vy * dt * 60
        
        # Top and bottom wall collision
        if self.y <= 0:
            self.y = 0
            self.vy = -self.vy
            self.add_screen_shake()
        elif self.y + self.size >= screen_height:
            self.y = screen_height - self.size
            self.vy = -self.vy
            self.add_screen_shake()
        
        # Left and right wall collision (scoring)
        if self.x <= 0:
            return "score_left"   # Balle sort à gauche - Player 2 (droite) scores
        elif self.x + self.size >= screen_width:
            return "score_right"  # Balle sort à droite - Player 1 (gauche) scores
        
        return None
    
    def update_visual_effects(self, dt):
        """Update visual effects"""
        # Smooth glow transition
        glow_diff = self.target_glow - self.glow_intensity
        self.glow_intensity += glow_diff * dt * 5
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt * 60
            if self.shake_duration <= 0:
                self.shake_intensity = 0
    
    def add_screen_shake(self):
        """Add screen shake effect"""
        self.shake_intensity = config.SCREEN_SHAKE_INTENSITY
        self.shake_duration = config.SCREEN_SHAKE_DURATION
    
    def collide_with_paddle(self, paddle):
        """Handle collision with paddle
        
        Args:
            paddle (Paddle): The paddle that was hit
            
        Returns:
            bool: True if collision occurred
        """
        if self.rect.colliderect(paddle.rect):
            # Calculate hit position on paddle (0.0 to 1.0)
            paddle_center_y = paddle.y + paddle.height // 2
            ball_center_y = self.y + self.size // 2
            hit_pos = (ball_center_y - paddle_center_y) / (paddle.height // 2)
            hit_pos = max(-1.0, min(1.0, hit_pos))  # Clamp to [-1, 1]
            
            # Calculate new angle based on hit position
            max_angle = math.radians(config.MAX_ANGLE_CHANGE)
            new_angle = hit_pos * max_angle
            
            # Determine direction based on which paddle was hit
            if paddle.player_id == 1:
                # Hit from left, go right
                direction = 1
                self.x = paddle.x + paddle.width
            else:
                # Hit from right, go left
                direction = -1
                self.x = paddle.x - self.size
            
            # Increase speed after each hit (10% per hit)
            self.hit_count += 1
            self.speed_multiplier = 1.0 + (self.hit_count * 0.1)
            current_speed = self.base_speed * self.speed_multiplier
            
            # Apply force multiplier if active
            if self.force_active:
                current_speed *= self.force_multiplier
            
            # Set new velocity with calculated speed
            self.vx = direction * current_speed * math.cos(new_angle)
            self.vy = current_speed * math.sin(new_angle)
            
            # Update speed property for compatibility
            self.speed = current_speed
            
            # Add screen shake
            self.add_screen_shake()
            
            return True
        
        return False
    
    def apply_force_push(self, player_id):
        """Apply force push effect
        
        Args:
            player_id (int): ID of player who used force push
        """
        current_time = pygame.time.get_ticks() / 1000.0
        
        print(f"💥 BALLE - Apply Force Push de joueur {player_id}")
        print(f"   Vitesse avant: vx={self.vx}, vy={self.vy}")
        
        self.force_active = True
        self.force_end_time = current_time + config.FORCE_EFFECT_DURATION
        self.force_multiplier = config.FORCE_MULTIPLIER
        self.force_player = player_id
        self.target_glow = 1.0
        
        # Increase speed dramatically - MULTIPLIER LA VITESSE
        old_vx = self.vx
        old_vy = self.vy
        self.vx *= config.FORCE_MULTIPLIER
        self.vy *= config.FORCE_MULTIPLIER
        
        print(f"   Vitesse après: vx={self.vx}, vy={self.vy}")
        print(f"   Multiplicateur: {config.FORCE_MULTIPLIER}")
        
        # Add strong screen shake
        self.shake_intensity = config.SCREEN_SHAKE_INTENSITY * 2
        self.shake_duration = config.SCREEN_SHAKE_DURATION * 2
    
    def draw(self, screen):
        """Draw the ball and its effects
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Draw trail
        if len(self.trail) > 1:
            for i, point in enumerate(self.trail):
                alpha = (i / len(self.trail)) * 255
                trail_color = (*config.NEON_YELLOW, int(alpha))
                
                # Create trail surface
                trail_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, trail_color, (self.size // 2, self.size // 2), self.size // 2)
                screen.blit(trail_surface, (point[0] - self.size // 2, point[1] - self.size // 2))
        
        # Draw glow effect
        if self.glow_intensity > 0:
            glow_size = int(self.glow_intensity * config.FORCE_GLOW_SIZE)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            
            # Color based on force player
            if self.force_player == 1:
                glow_color = (*config.NEON_BLUE, int(self.glow_intensity * 150))
            else:
                glow_color = (*config.NEON_PINK, int(self.glow_intensity * 150))
            
            pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
            
            glow_x = self.x + self.size // 2 - glow_size
            glow_y = self.y + self.size // 2 - glow_size
            screen.blit(glow_surface, (glow_x, glow_y))
        
        # Draw main ball
        ball_color = config.NEON_YELLOW
        if self.force_active:
            # Brighten when force is active
            ball_color = tuple(min(255, int(c * 1.5)) for c in config.NEON_YELLOW)
        
        pygame.draw.circle(screen, ball_color, 
                          (int(self.x + self.size // 2), int(self.y + self.size // 2)), 
                          self.size // 2)
        
        # Draw force effect indicator
        if self.force_active:
            # Draw speed lines
            for i in range(5):
                line_x = self.x + self.size // 2
                line_y = self.y + self.size // 2
                line_length = 20 + i * 5
                line_angle = math.atan2(self.vy, self.vx)
                
                end_x = line_x + math.cos(line_angle) * line_length
                end_y = line_y + math.sin(line_angle) * line_length
                
                pygame.draw.line(screen, config.NEON_YELLOW, (line_x, line_y), (end_x, end_y), 2)
    
    def get_screen_shake(self):
        """Get current screen shake offset
        
        Returns:
            tuple: (x_offset, y_offset)
        """
        if self.shake_intensity > 0:
            x_offset = random.uniform(-self.shake_intensity, self.shake_intensity)
            y_offset = random.uniform(-self.shake_intensity, self.shake_intensity)
            return (int(x_offset), int(y_offset))
        return (0, 0)
    
    def get_state(self):
        """Get ball state for networking
        
        Returns:
            dict: Ball state data
        """
        return {
            'x': self.x,
            'y': self.y,
            'vx': self.vx,
            'vy': self.vy,
            'speed': self.speed,
            'base_speed': self.base_speed,
            'speed_multiplier': self.speed_multiplier,
            'hit_count': self.hit_count,
            'force_active': self.force_active,
            'force_multiplier': self.force_multiplier,
            'force_player': self.force_player,
            'glow_intensity': self.glow_intensity
        }
    
    def set_state(self, state):
        """Set ball state from network data
        
        Args:
            state (dict): Ball state data
        """
        self.x = state['x']
        self.y = state['y']
        self.vx = state['vx']
        self.vy = state['vy']
        self.speed = state['speed']
        
        # Handle speed tracking if available
        if 'base_speed' in state:
            self.base_speed = state['base_speed']
        if 'speed_multiplier' in state:
            self.speed_multiplier = state['speed_multiplier']
        if 'hit_count' in state:
            self.hit_count = state['hit_count']
        
        self.force_active = state['force_active']
        self.force_multiplier = state['force_multiplier']
        self.force_player = state['force_player']
        self.glow_intensity = state['glow_intensity']
