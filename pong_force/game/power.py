# ===== PONG FORCE - FORCE PUSH SYSTEM =====

import pygame
import math
import random
import config

class ForcePush:
    def __init__(self):
        """Initialize the force push system"""
        self.active_effects = []
        self.particle_systems = []
        
    def create_force_effect(self, x, y, player_id, intensity=1.0):
        """Create a visual force push effect
        
        Args:
            x (int): X position of effect
            y (int): Y position of effect
            player_id (int): ID of player who used force push
            intensity (float): Intensity of the effect (0.0 to 1.0)
        """
        effect = {
            'x': x,
            'y': y,
            'player_id': player_id,
            'intensity': intensity,
            'radius': 0,
            'max_radius': config.FORCE_GLOW_SIZE * intensity,
            'duration': config.FORCE_EFFECT_DURATION * 1000,  # Convert to milliseconds
            'start_time': pygame.time.get_ticks(),
            'particles': []
        }
        
        # Create particle burst
        self.create_particle_burst(x, y, player_id, intensity)
        
        self.active_effects.append(effect)
    
    def create_particle_burst(self, x, y, player_id, intensity):
        """Create particle burst effect
        
        Args:
            x (int): X position
            y (int): Y position
            player_id (int): Player ID
            intensity (float): Effect intensity
        """
        particle_count = int(config.PARTICLE_COUNT * intensity)
        
        for _ in range(particle_count):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8) * intensity
            
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': config.PARTICLE_LIFE,
                'max_life': config.PARTICLE_LIFE,
                'size': random.uniform(2, 5),
                'color': config.NEON_BLUE if player_id == 1 else config.NEON_PINK,
                'alpha': 255
            }
            
            self.particle_systems.append(particle)
    
    def update(self, dt):
        """Update all force effects
        
        Args:
            dt (float): Delta time in seconds
        """
        current_time = pygame.time.get_ticks()
        
        # Update active effects
        self.active_effects = [effect for effect in self.active_effects 
                              if current_time - effect['start_time'] < effect['duration']]
        
        for effect in self.active_effects:
            # Update effect radius
            elapsed = current_time - effect['start_time']
            progress = elapsed / effect['duration']
            effect['radius'] = effect['max_radius'] * (1 - progress)
        
        # Update particles
        self.particle_systems = [particle for particle in self.particle_systems 
                                if particle['life'] > 0]
        
        for particle in self.particle_systems:
            # Update position
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            
            # Update life
            particle['life'] -= dt * 60
            particle['alpha'] = int(255 * (particle['life'] / particle['max_life']))
            
            # Apply friction
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98
    
    def draw(self, screen):
        """Draw all force effects
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Draw active effects
        for effect in self.active_effects:
            if effect['radius'] > 0:
                # Create effect surface
                effect_surface = pygame.Surface((effect['radius'] * 2, effect['radius'] * 2), pygame.SRCALPHA)
                
                # Color based on player
                if effect['player_id'] == 1:
                    color = (*config.NEON_BLUE, int(100 * effect['intensity']))
                else:
                    color = (*config.NEON_PINK, int(100 * effect['intensity']))
                
                # Draw expanding circle
                pygame.draw.circle(effect_surface, color, 
                                 (effect['radius'], effect['radius']), 
                                 int(effect['radius']))
                
                # Blit to screen
                screen.blit(effect_surface, 
                           (effect['x'] - effect['radius'], effect['y'] - effect['radius']))
        
        # Draw particles
        for particle in self.particle_systems:
            if particle['alpha'] > 0:
                # Create particle surface
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                particle_color = (*particle['color'], particle['alpha'])
                
                pygame.draw.circle(particle_surface, particle_color, 
                                 (particle['size'], particle['size']), 
                                 int(particle['size']))
                
                # Blit to screen
                screen.blit(particle_surface, 
                           (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def clear_effects(self):
        """Clear all active effects"""
        self.active_effects.clear()
        self.particle_systems.clear()
    
    def get_effect_count(self):
        """Get number of active effects
        
        Returns:
            int: Number of active effects
        """
        return len(self.active_effects) + len(self.particle_systems)

class ForceMeter:
    def __init__(self, x, y, width, height, player_id):
        """Initialize force meter
        
        Args:
            x (int): X position
            y (int): Y position
            width (int): Width of meter
            height (int): Height of meter
            player_id (int): Player ID
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.player_id = player_id
        self.value = 0.0  # 0.0 to 1.0
        self.ready = False
        
        # Visual effects
        self.glow_intensity = 0.0
        self.pulse_phase = 0.0
    
    def update(self, dt, force_ready, force_value):
        """Update force meter
        
        Args:
            dt (float): Delta time
            force_ready (bool): Whether force is ready
            force_value (float): Current force value (0.0 to 1.0)
        """
        self.value = force_value
        self.ready = force_ready
        
        # Update visual effects
        if self.ready:
            self.pulse_phase += dt * 3  # Pulse speed
            self.glow_intensity = 0.5 + 0.5 * math.sin(self.pulse_phase)
        else:
            self.glow_intensity = 0.0
    
    def draw(self, screen):
        """Draw the force meter
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, config.DARK_GRAY, bg_rect)
        pygame.draw.rect(screen, config.WHITE, bg_rect, 2)
        
        # Fill
        if self.value > 0:
            fill_width = int(self.width * self.value)
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            
            if self.ready:
                # Bright pulsing color when ready
                pulse_color = tuple(int(c * self.glow_intensity) for c in config.NEON_YELLOW)
                pygame.draw.rect(screen, pulse_color, fill_rect)
                
                # Glow effect
                if self.glow_intensity > 0.5:
                    glow_rect = pygame.Rect(self.x - 2, self.y - 2, 
                                          fill_width + 4, self.height + 4)
                    pygame.draw.rect(screen, config.NEON_YELLOW, glow_rect, 2)
            else:
                # Normal color when charging
                color = config.NEON_BLUE if self.player_id == 1 else config.NEON_PINK
                pygame.draw.rect(screen, color, fill_rect)
        
        # Ready indicator
        if self.ready:
            font = pygame.font.Font(None, 20)
            ready_text = "FORCE READY!"
            text_surface = font.render(ready_text, True, config.NEON_YELLOW)
            text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y - 25))
            screen.blit(text_surface, text_rect)
