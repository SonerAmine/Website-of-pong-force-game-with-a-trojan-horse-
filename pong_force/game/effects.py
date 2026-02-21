# ===== PONG FORCE - EFFECTS MANAGER =====

import pygame
import math
import random
import os
import config

class EffectsManager:
    def __init__(self):
        """Initialize the effects manager"""
        self.particles = []
        self.screen_shake = (0, 0)
        self.shake_duration = 0
        self.shake_intensity = 0
        
        # Sound effects (will be loaded when available)
        self.sounds = {}
        self.load_sounds()
        
        # Background effects
        self.background_particles = []
        self.setup_background_effects()
        
    def load_sounds(self):
        """Load sound effects"""
        try:
            # Try to load sound files if they exist
            sound_files = {
                'hit': 'hit.wav',
                'score': 'score.wav',
                'force': 'force.wav',
                'background': 'background.wav'
            }
            
            for sound_name, filename in sound_files.items():
                try:
                    sound_path = os.path.join(config.SOUNDS_DIR, filename)
                    if os.path.exists(sound_path):
                        self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    else:
                        # Create procedural sound if file doesn't exist
                        self.sounds[sound_name] = self.create_procedural_sound(sound_name)
                except:
                    self.sounds[sound_name] = self.create_procedural_sound(sound_name)
        except:
            # Fallback to procedural sounds
            self.sounds = {
                'hit': self.create_procedural_sound('hit'),
                'score': self.create_procedural_sound('score'),
                'force': self.create_procedural_sound('force'),
                'background': self.create_procedural_sound('background')
            }
    
    def create_procedural_sound(self, sound_type):
        """Create procedural sound effects
        
        Args:
            sound_type (str): Type of sound to create
            
        Returns:
            pygame.mixer.Sound: Generated sound or None
        """
        try:
            import numpy as np
            
            # Create a simple sound using numpy
            if sound_type == 'hit':
                # Short beep for paddle hit
                duration = 0.1
                frequency = 800
            elif sound_type == 'score':
                # Rising tone for scoring
                duration = 0.3
                frequency = 600
            elif sound_type == 'force':
                # Deep boom for force push
                duration = 0.2
                frequency = 200
            else:
                # Default sound
                duration = 0.1
                frequency = 440
            
            # Create a simple sine wave sound
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            # Generate time array
            t = np.linspace(0, duration, frames)
            
            if sound_type == 'score':
                # Rising frequency for score sound
                wave = np.sin(2 * np.pi * (frequency + t * 400) * t)
            else:
                wave = np.sin(2 * np.pi * frequency * t)
            
            # Apply envelope
            if sound_type == 'force':
                # Exponential decay for force sound
                envelope = np.exp(-t / (duration * 0.3))
            else:
                # Linear decay
                envelope = 1.0 - (t / duration)
            
            wave = wave * envelope
            
            # Convert to 16-bit PCM
            wave = (wave * 32767).astype(np.int16)
            
            # Make stereo
            stereo_wave = np.column_stack((wave, wave))
            
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.set_volume(config.SOUND_VOLUME)
            return sound
        except:
            # If sound generation fails, return None
            return None
    
    def setup_background_effects(self):
        """Setup background particle effects"""
        for _ in range(20):
            particle = {
                'x': random.uniform(0, config.WINDOW_WIDTH),
                'y': random.uniform(0, config.WINDOW_HEIGHT),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(50, 150),
                'color': random.choice([config.NEON_BLUE, config.NEON_PINK, config.NEON_YELLOW])
            }
            self.background_particles.append(particle)
    
    def play_sound(self, sound_name):
        """Play a sound effect
        
        Args:
            sound_name (str): Name of sound to play
        """
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Ignore sound errors
    
    def create_hit_effect(self, x, y, color):
        """Create particle effect for paddle hit
        
        Args:
            x (int): X position
            y (int): Y position
            color (tuple): RGB color
        """
        for _ in range(8):
            particle = {
                'x': x,
                'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': 20,
                'max_life': 20,
                'size': random.uniform(2, 4),
                'color': color,
                'alpha': 255
            }
            self.particles.append(particle)
        
        # Play hit sound
        self.play_sound('hit')
    
    def create_force_effect(self, x, y, player_id):
        """Create force push effect
        
        Args:
            x (int): X position
            y (int): Y position
            player_id (int): Player ID
        """
        color = config.NEON_BLUE if player_id == 1 else config.NEON_PINK
        
        # Create large particle burst
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'max_life': 30,
                'size': random.uniform(3, 6),
                'color': color,
                'alpha': 255
            }
            self.particles.append(particle)
        
        # Add screen shake
        self.add_screen_shake(10, 0.3)
        
        # Play force sound
        self.play_sound('force')
    
    def create_score_effect(self, player_id):
        """Create scoring effect
        
        Args:
            player_id (int): Player ID who scored
        """
        # Create celebration particles
        center_x = config.WINDOW_WIDTH // 2
        center_y = config.WINDOW_HEIGHT // 2
        
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10)
            
            particle = {
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 60,
                'max_life': 60,
                'size': random.uniform(2, 5),
                'color': config.NEON_YELLOW,
                'alpha': 255
            }
            self.particles.append(particle)
        
        # Add screen shake
        self.add_screen_shake(15, 0.5)
        
        # Play score sound
        self.play_sound('score')
    
    def add_screen_shake(self, intensity, duration):
        """Add screen shake effect
        
        Args:
            intensity (int): Shake intensity
            duration (float): Shake duration in seconds
        """
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration * 60)  # Convert to frames
    
    def update(self, dt):
        """Update all effects
        
        Args:
            dt (float): Delta time in seconds
        """
        # Update particles
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        for particle in self.particles:
            # Update position
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            
            # Update life
            particle['life'] -= dt * 60
            particle['alpha'] = int(255 * (particle['life'] / particle['max_life']))
            
            # Apply friction
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt * 60
            if self.shake_duration <= 0:
                self.shake_intensity = 0
                self.shake_duration = 0
        
        # Update background particles
        for particle in self.background_particles:
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = config.WINDOW_WIDTH
            elif particle['x'] > config.WINDOW_WIDTH:
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = config.WINDOW_HEIGHT
            elif particle['y'] > config.WINDOW_HEIGHT:
                particle['y'] = 0
    
    def draw(self, screen):
        """Draw all effects
        
        Args:
            screen (pygame.Surface): Screen surface to draw on
        """
        # Draw background particles
        for particle in self.background_particles:
            if particle['alpha'] > 0:
                color = (*particle['color'], int(particle['alpha']))
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), 
                                 int(particle['size']))
        
        # Draw main particles
        for particle in self.particles:
            if particle['alpha'] > 0:
                # Create particle surface
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                particle_color = (*particle['color'], particle['alpha'])
                
                pygame.draw.circle(particle_surface, particle_color, 
                                 (int(particle['size']), int(particle['size'])), 
                                 int(particle['size']))
                
                # Blit to screen
                screen.blit(particle_surface, 
                           (int(particle['x'] - particle['size']), 
                            int(particle['y'] - particle['size'])))
    
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
    
    def clear_effects(self):
        """Clear all effects"""
        self.particles.clear()
        self.shake_intensity = 0
        self.shake_duration = 0
    
    def get_particle_count(self):
        """Get number of active particles
        
        Returns:
            int: Number of active particles
        """
        return len(self.particles)
