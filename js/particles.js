// ===== PARTICLE SYSTEM FOR PONG FORCE WEBSITE =====

class ParticleSystem {
    constructor(container) {
        this.container = container;
        this.particles = [];
        this.particleCount = 50;
        this.animationId = null;
        this.isRunning = false;
        
        this.init();
    }
    
    init() {
        this.createParticles();
        this.start();
    }
    
    createParticles() {
        // Clear existing particles
        this.container.innerHTML = '';
        this.particles = [];
        
        for (let i = 0; i < this.particleCount; i++) {
            this.createParticle();
        }
    }
    
    createParticle() {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random properties
        const size = Math.random() * 4 + 1;
        const x = Math.random() * window.innerWidth;
        const y = Math.random() * window.innerHeight;
        const colors = ['#00FFFF', '#FF00CC', '#FFD700', '#FFFFFF'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        const opacity = Math.random() * 0.6 + 0.2;
        
        // Set initial position and style
        particle.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            border-radius: 50%;
            left: ${x}px;
            top: ${y}px;
            opacity: ${opacity};
            box-shadow: 0 0 ${size * 3}px ${color};
            pointer-events: none;
            transition: opacity 0.3s ease;
        `;
        
        this.container.appendChild(particle);
        
        // Store particle data
        const particleData = {
            element: particle,
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 0.8,
            vy: (Math.random() - 0.5) * 0.8,
            size: size,
            color: color,
            opacity: opacity,
            pulsePhase: Math.random() * Math.PI * 2,
            pulseSpeed: Math.random() * 0.02 + 0.01
        };
        
        this.particles.push(particleData);
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.animate();
    }
    
    stop() {
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
    
    animate() {
        if (!this.isRunning) return;
        
        this.particles.forEach(particle => {
            this.updateParticle(particle);
        });
        
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    updateParticle(particle) {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;
        
        // Update pulse phase
        particle.pulsePhase += particle.pulseSpeed;
        
        // Wrap around screen
        if (particle.x < -particle.size) {
            particle.x = window.innerWidth + particle.size;
        }
        if (particle.x > window.innerWidth + particle.size) {
            particle.x = -particle.size;
        }
        if (particle.y < -particle.size) {
            particle.y = window.innerHeight + particle.size;
        }
        if (particle.y > window.innerHeight + particle.size) {
            particle.y = -particle.size;
        }
        
        // Calculate pulsing opacity
        const pulseOpacity = 0.3 + 0.4 * Math.sin(particle.pulsePhase);
        const finalOpacity = particle.opacity * pulseOpacity;
        
        // Apply transformations
        particle.element.style.left = particle.x + 'px';
        particle.element.style.top = particle.y + 'px';
        particle.element.style.opacity = finalOpacity;
        
        // Update glow effect
        const glowSize = particle.size * 3 + Math.sin(particle.pulsePhase) * 2;
        particle.element.style.boxShadow = `0 0 ${glowSize}px ${particle.color}`;
    }
    
    // Add interactive particle on mouse move
    addInteractiveParticle(x, y) {
        const particle = document.createElement('div');
        particle.className = 'interactive-particle';
        
        const size = Math.random() * 6 + 3;
        const colors = ['#00FFFF', '#FF00CC', '#FFD700'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        particle.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            background: ${color};
            border-radius: 50%;
            left: ${x}px;
            top: ${y}px;
            opacity: 0.8;
            box-shadow: 0 0 ${size * 4}px ${color};
            pointer-events: none;
            z-index: 1000;
        `;
        
        this.container.appendChild(particle);
        
        // Animate particle expansion and fade
        let scale = 0;
        let opacity = 0.8;
        
        const animate = () => {
            scale += 0.1;
            opacity -= 0.02;
            
            particle.style.transform = `scale(${scale})`;
            particle.style.opacity = opacity;
            
            if (opacity > 0) {
                requestAnimationFrame(animate);
            } else {
                particle.remove();
            }
        };
        
        animate();
    }
    
    // Resize handler
    resize() {
        this.particles.forEach(particle => {
            // Keep particles within bounds
            if (particle.x > window.innerWidth) {
                particle.x = window.innerWidth;
            }
            if (particle.y > window.innerHeight) {
                particle.y = window.innerHeight;
            }
        });
    }
    
    // Update particle count
    setParticleCount(count) {
        this.particleCount = Math.max(10, Math.min(200, count));
        this.createParticles();
    }
    
    // Get current particle count
    getParticleCount() {
        return this.particles.length;
    }
}

// ===== PARTICLE CONNECTIONS =====
class ParticleConnections {
    constructor(particleSystem) {
        this.particleSystem = particleSystem;
        this.canvas = null;
        this.ctx = null;
        this.maxDistance = 150;
        this.lineOpacity = 0.1;
        
        this.init();
    }
    
    init() {
        this.createCanvas();
        this.start();
    }
    
    createCanvas() {
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        `;
        
        this.ctx = this.canvas.getContext('2d');
        this.particleSystem.container.appendChild(this.canvas);
        
        this.resize();
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    start() {
        this.animate();
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const particles = this.particleSystem.particles;
        
        // Draw connections between nearby particles
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < this.maxDistance) {
                    const opacity = (1 - distance / this.maxDistance) * this.lineOpacity;
                    
                    this.ctx.strokeStyle = `rgba(0, 255, 255, ${opacity})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    this.ctx.moveTo(particles[i].x, particles[i].y);
                    this.ctx.lineTo(particles[j].x, particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

// ===== INITIALIZATION =====
let particleSystem = null;
let particleConnections = null;

function initializeParticleSystem() {
    const container = document.getElementById('particles-container');
    if (!container) return;
    
    // Create particle system
    particleSystem = new ParticleSystem(container);
    
    // Create particle connections
    particleConnections = new ParticleConnections(particleSystem);
    
    // Add mouse interaction
    document.addEventListener('mousemove', (e) => {
        if (Math.random() < 0.1) { // 10% chance to create particle on mouse move
            particleSystem.addInteractiveParticle(e.clientX, e.clientY);
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', debounce(() => {
        particleSystem.resize();
        particleConnections.resize();
    }, 250));
}

// ===== UTILITY FUNCTIONS =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== PERFORMANCE MONITORING =====
class PerformanceMonitor {
    constructor() {
        this.fps = 0;
        this.frameCount = 0;
        this.lastTime = performance.now();
    }
    
    update() {
        this.frameCount++;
        const currentTime = performance.now();
        
        if (currentTime - this.lastTime >= 1000) {
            this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
            this.frameCount = 0;
            this.lastTime = currentTime;
            
            // Adjust particle count based on performance
            if (particleSystem) {
                if (this.fps < 30 && particleSystem.getParticleCount() > 20) {
                    particleSystem.setParticleCount(particleSystem.getParticleCount() - 10);
                } else if (this.fps > 50 && particleSystem.getParticleCount() < 100) {
                    particleSystem.setParticleCount(particleSystem.getParticleCount() + 10);
                }
            }
        }
    }
}

// ===== AUTO-INITIALIZE =====
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for the page to load
    setTimeout(initializeParticleSystem, 100);
});

// ===== EXPORT FOR MODULE USAGE =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ParticleSystem,
        ParticleConnections,
        initializeParticleSystem
    };
}
