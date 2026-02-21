// ===== PONG FORCE DEMO GAME =====

class PongDemo {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas not found:', canvasId);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.isRunning = false;
        this.animationId = null;
        
        // Game settings
        this.canvas.width = 800;
        this.canvas.height = 400;
        
        // Game objects
        this.ball = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2,
            vx: 4,
            vy: 2,
            radius: 8,
            color: '#FFD700',
            trail: [],
            baseSpeed: 4,
            speedMultiplier: 1,
            hitCount: 0
        };
        
        this.paddle1 = {
            x: 20,
            y: this.canvas.height / 2 - 50,
            width: 15,
            height: 100,
            speed: 5,
            color: '#00FFFF',
            score: 0
        };
        
        this.paddle2 = {
            x: this.canvas.width - 35,
            y: this.canvas.height / 2 - 50,
            width: 15,
            height: 100,
            speed: 5,
            color: '#FF00CC',
            score: 0
        };
        
        // Force Push mechanics
        this.forcePush = {
            active: false,
            duration: 0,
            maxDuration: 60, // 1 second at 60fps
            multiplier: 2.5,
            cooldown: 0,
            maxCooldown: 180, // 3 seconds at 60fps
            player1Used: false,
            player2Used: false
        };
        
        // Input handling
        this.keys = {};
        this.setupInput();
        
        // Game state
        this.gameState = 'waiting'; // waiting, playing, paused, gameOver
        this.winner = null;
        this.maxScore = 5;
        
        // Visual effects
        this.particles = [];
        this.forceEffect = {
            active: false,
            x: 0,
            y: 0,
            radius: 0,
            maxRadius: 100,
            duration: 0,
            maxDuration: 30
        };
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.resetGame();
    }
    
    setupCanvas() {
        // Make canvas responsive
        const container = this.canvas.parentElement;
        const resizeCanvas = () => {
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight;
            
            // Maintain aspect ratio
            const aspectRatio = 800 / 400;
            let newWidth = containerWidth;
            let newHeight = containerWidth / aspectRatio;
            
            if (newHeight > containerHeight) {
                newHeight = containerHeight;
                newWidth = containerHeight * aspectRatio;
            }
            
            this.canvas.style.width = newWidth + 'px';
            this.canvas.style.height = newHeight + 'px';
        };
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
    }
    
    setupInput() {
        document.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            
            // Handle Force Push for Player 1 (Space)
            if (e.code === 'Space' && 
                this.gameState === 'playing' && 
                this.forcePush.cooldown <= 0 &&
                !this.forcePush.player1Used) {
                this.activateForcePush();
            }
            
            // Handle Force Push for Player 2 (Shift)
            if ((e.code === 'ShiftLeft' || e.code === 'ShiftRight') && 
                this.gameState === 'playing' && 
                this.forcePush.cooldown <= 0 &&
                !this.forcePush.player2Used) {
                this.activateForcePush();
            }
            
            // Handle game start
            if (e.code === 'Space' && this.gameState === 'waiting') {
                this.startGame();
            }
            
            // Handle pause
            if (e.code === 'Escape') {
                this.togglePause();
            }
        });
        
        document.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });
    }
    
    startGame() {
        this.gameState = 'playing';
        this.isRunning = true;
        this.gameLoop();
    }
    
    togglePause() {
        if (this.gameState === 'playing') {
            this.gameState = 'paused';
            this.isRunning = false;
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
            }
        } else if (this.gameState === 'paused') {
            this.gameState = 'playing';
            this.isRunning = true;
            this.gameLoop();
        }
    }
    
    resetGame() {
        this.ball.x = this.canvas.width / 2;
        this.ball.y = this.canvas.height / 2;
        this.ball.vx = (Math.random() > 0.5 ? 1 : -1) * this.ball.baseSpeed;
        this.ball.vy = (Math.random() - 0.5) * this.ball.baseSpeed;
        this.ball.trail = [];
        this.ball.speedMultiplier = 1;
        this.ball.hitCount = 0;
        
        this.paddle1.y = this.canvas.height / 2 - 50;
        this.paddle2.y = this.canvas.height / 2 - 50;
        
        this.forcePush.active = false;
        this.forcePush.duration = 0;
        this.forcePush.cooldown = 0;
        this.forcePush.player1Used = false;
        this.forcePush.player2Used = false;
        
        this.particles = [];
        this.forceEffect.active = false;
        
        this.gameState = 'waiting';
        this.winner = null;
    }
    
    activateForcePush() {
        // Check if player has special shot available
        const player1CanUse = !this.forcePush.player1Used && (this.keys['Space']);
        const player2CanUse = !this.forcePush.player2Used && (this.keys['ShiftLeft'] || this.keys['ShiftRight']);
        
        if (!player1CanUse && !player2CanUse) return;
        
        this.forcePush.active = true;
        this.forcePush.duration = this.forcePush.maxDuration;
        this.forcePush.cooldown = this.forcePush.maxCooldown;
        
        // Mark special shot as used for the respective player
        if (player1CanUse) {
            this.forcePush.player1Used = true;
        } else if (player2CanUse) {
            this.forcePush.player2Used = true;
        }
        
        // Create force effect
        this.forceEffect.active = true;
        this.forceEffect.x = this.ball.x;
        this.forceEffect.y = this.ball.y;
        this.forceEffect.radius = 0;
        this.forceEffect.duration = this.forceEffect.maxDuration;
        
        // Create particles
        this.createForceParticles();
        
        // Play sound effect
        this.playForceSound();
    }
    
    createForceParticles() {
        for (let i = 0; i < 20; i++) {
            this.particles.push({
                x: this.ball.x,
                y: this.ball.y,
                vx: (Math.random() - 0.5) * 10,
                vy: (Math.random() - 0.5) * 10,
                life: 30,
                maxLife: 30,
                color: Math.random() > 0.5 ? '#00FFFF' : '#FF00CC'
            });
        }
    }
    
    playForceSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
            oscillator.frequency.exponentialRampToValueAtTime(800, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (error) {
            console.log('Audio not supported');
        }
    }
    
    update() {
        if (this.gameState !== 'playing') return;
        
        this.updatePaddles();
        this.updateBall();
        this.updateForcePush();
        this.updateParticles();
        this.updateForceEffect();
        this.checkCollisions();
        this.checkScore();
    }
    
    updatePaddles() {
        // Player 1 (Arrow keys)
        if (this.keys['ArrowUp'] && this.paddle1.y > 0) {
            this.paddle1.y -= this.paddle1.speed;
        }
        if (this.keys['ArrowDown'] && this.paddle1.y < this.canvas.height - this.paddle1.height) {
            this.paddle1.y += this.paddle1.speed;
        }
        
        // Player 2 (W/S keys)
        if (this.keys['KeyW'] && this.paddle2.y > 0) {
            this.paddle2.y -= this.paddle2.speed;
        }
        if (this.keys['KeyS'] && this.paddle2.y < this.canvas.height - this.paddle2.height) {
            this.paddle2.y += this.paddle2.speed;
        }
    }
    
    updateBall() {
        // Add ball to trail
        this.ball.trail.push({ x: this.ball.x, y: this.ball.y });
        if (this.ball.trail.length > 10) {
            this.ball.trail.shift();
        }
        
        // Update ball position
        this.ball.x += this.ball.vx;
        this.ball.y += this.ball.vy;
        
        // Bounce off top and bottom walls
        if (this.ball.y - this.ball.radius <= 0 || this.ball.y + this.ball.radius >= this.canvas.height) {
            this.ball.vy = -this.ball.vy;
            this.ball.y = Math.max(this.ball.radius, Math.min(this.canvas.height - this.ball.radius, this.ball.y));
        }
    }
    
    updateForcePush() {
        if (this.forcePush.active) {
            this.forcePush.duration--;
            if (this.forcePush.duration <= 0) {
                this.forcePush.active = false;
            }
        }
        
        if (this.forcePush.cooldown > 0) {
            this.forcePush.cooldown--;
        }
    }
    
    updateParticles() {
        this.particles = this.particles.filter(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.life--;
            particle.vx *= 0.98;
            particle.vy *= 0.98;
            return particle.life > 0;
        });
    }
    
    updateForceEffect() {
        if (this.forceEffect.active) {
            this.forceEffect.duration--;
            this.forceEffect.radius = (1 - this.forceEffect.duration / this.forceEffect.maxDuration) * this.forceEffect.maxRadius;
            
            if (this.forceEffect.duration <= 0) {
                this.forceEffect.active = false;
            }
        }
    }
    
    checkCollisions() {
        // Paddle 1 collision
        if (this.ball.x - this.ball.radius <= this.paddle1.x + this.paddle1.width &&
            this.ball.x + this.ball.radius >= this.paddle1.x &&
            this.ball.y >= this.paddle1.y &&
            this.ball.y <= this.paddle1.y + this.paddle1.height &&
            this.ball.vx < 0) {
            
            this.ball.vx = Math.abs(this.ball.vx) * this.ball.speedMultiplier;
            this.ball.x = this.paddle1.x + this.paddle1.width + this.ball.radius;
            
            // Add spin based on where ball hits paddle
            const hitPos = (this.ball.y - this.paddle1.y) / this.paddle1.height;
            this.ball.vy += (hitPos - 0.5) * 8;
            
            // Increase speed after each hit
            this.ball.hitCount++;
            this.ball.speedMultiplier = 1 + (this.ball.hitCount * 0.1); // 10% increase per hit
            
            // Apply Force Push multiplier if active
            if (this.forcePush.active) {
                this.ball.vx *= this.forcePush.multiplier;
                this.ball.vy *= this.forcePush.multiplier;
            }
            
            this.createHitParticles(this.paddle1.color);
        }
        
        // Paddle 2 collision
        if (this.ball.x + this.ball.radius >= this.paddle2.x &&
            this.ball.x - this.ball.radius <= this.paddle2.x + this.paddle2.width &&
            this.ball.y >= this.paddle2.y &&
            this.ball.y <= this.paddle2.y + this.paddle2.height &&
            this.ball.vx > 0) {
            
            this.ball.vx = -Math.abs(this.ball.vx) * this.ball.speedMultiplier;
            this.ball.x = this.paddle2.x - this.ball.radius;
            
            // Add spin based on where ball hits paddle
            const hitPos = (this.ball.y - this.paddle2.y) / this.paddle2.height;
            this.ball.vy += (hitPos - 0.5) * 8;
            
            // Increase speed after each hit
            this.ball.hitCount++;
            this.ball.speedMultiplier = 1 + (this.ball.hitCount * 0.1); // 10% increase per hit
            
            // Apply Force Push multiplier if active
            if (this.forcePush.active) {
                this.ball.vx *= this.forcePush.multiplier;
                this.ball.vy *= this.forcePush.multiplier;
            }
            
            this.createHitParticles(this.paddle2.color);
        }
    }
    
    createHitParticles(color) {
        for (let i = 0; i < 8; i++) {
            this.particles.push({
                x: this.ball.x,
                y: this.ball.y,
                vx: (Math.random() - 0.5) * 6,
                vy: (Math.random() - 0.5) * 6,
                life: 20,
                maxLife: 20,
                color: color
            });
        }
    }
    
    checkScore() {
        // Player 1 scores
        if (this.ball.x > this.canvas.width) {
            this.paddle1.score++;
            this.resetBall();
            if (this.paddle1.score >= this.maxScore) {
                this.endGame(1);
            }
        }
        
        // Player 2 scores
        if (this.ball.x < 0) {
            this.paddle2.score++;
            this.resetBall();
            if (this.paddle2.score >= this.maxScore) {
                this.endGame(2);
            }
        }
    }
    
    resetBall() {
        this.ball.x = this.canvas.width / 2;
        this.ball.y = this.canvas.height / 2;
        this.ball.vx = (Math.random() > 0.5 ? 1 : -1) * this.ball.baseSpeed;
        this.ball.vy = (Math.random() - 0.5) * this.ball.baseSpeed;
        this.ball.trail = [];
        
        // Reset speed to initial when someone scores
        this.ball.speedMultiplier = 1;
        this.ball.hitCount = 0;
        
        this.forcePush.active = false;
        this.forcePush.duration = 0;
        this.forcePush.cooldown = 0;
        
        this.particles = [];
        this.forceEffect.active = false;
    }
    
    endGame(winner) {
        this.gameState = 'gameOver';
        this.winner = winner;
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
    
    render() {
        // Clear canvas
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw center line
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([10, 10]);
        this.ctx.beginPath();
        this.ctx.moveTo(this.canvas.width / 2, 0);
        this.ctx.lineTo(this.canvas.width / 2, this.canvas.height);
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Draw ball trail
        this.ball.trail.forEach((point, index) => {
            const alpha = index / this.ball.trail.length;
            this.ctx.fillStyle = `rgba(255, 215, 0, ${alpha * 0.5})`;
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, this.ball.radius * alpha, 0, Math.PI * 2);
            this.ctx.fill();
        });
        
        // Draw ball
        this.ctx.fillStyle = this.ball.color;
        this.ctx.shadowColor = this.ball.color;
        this.ctx.shadowBlur = 20;
        this.ctx.beginPath();
        this.ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.shadowBlur = 0;
        
        // Draw paddles
        this.drawPaddle(this.paddle1);
        this.drawPaddle(this.paddle2);
        
        // Draw force effect
        if (this.forceEffect.active) {
            this.ctx.strokeStyle = `rgba(255, 0, 204, ${1 - this.forceEffect.duration / this.forceEffect.maxDuration})`;
            this.ctx.lineWidth = 3;
            this.ctx.beginPath();
            this.ctx.arc(this.forceEffect.x, this.forceEffect.y, this.forceEffect.radius, 0, Math.PI * 2);
            this.ctx.stroke();
        }
        
        // Draw particles
        this.particles.forEach(particle => {
            const alpha = particle.life / particle.maxLife;
            this.ctx.fillStyle = particle.color + Math.floor(alpha * 255).toString(16).padStart(2, '0');
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, 3, 0, Math.PI * 2);
            this.ctx.fill();
        });
        
        // Draw UI
        this.drawUI();
    }
    
    drawPaddle(paddle) {
        this.ctx.fillStyle = paddle.color;
        this.ctx.shadowColor = paddle.color;
        this.ctx.shadowBlur = 15;
        this.ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
        this.ctx.shadowBlur = 0;
    }
    
    drawUI() {
        // Draw scores
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = 'bold 24px Orbitron, monospace';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(this.paddle1.score, this.canvas.width / 4, 50);
        this.ctx.fillText(this.paddle2.score, 3 * this.canvas.width / 4, 50);
        
        // Draw force push indicators
        // Player 1 special shot indicator
        if (!this.forcePush.player1Used) {
            this.ctx.fillStyle = '#00FFFF';
            this.ctx.font = '12px Orbitron, monospace';
            this.ctx.textAlign = 'left';
            this.ctx.fillText('P1: SPACE (Special)', 10, 30);
        } else {
            this.ctx.fillStyle = 'rgba(0, 255, 255, 0.3)';
            this.ctx.font = '12px Orbitron, monospace';
            this.ctx.textAlign = 'left';
            this.ctx.fillText('P1: Used', 10, 30);
        }
        
        // Player 2 special shot indicator
        if (!this.forcePush.player2Used) {
            this.ctx.fillStyle = '#FF00CC';
            this.ctx.font = '12px Orbitron, monospace';
            this.ctx.textAlign = 'right';
            this.ctx.fillText('P2: SHIFT (Special)', this.canvas.width - 10, 30);
        } else {
            this.ctx.fillStyle = 'rgba(255, 0, 204, 0.3)';
            this.ctx.font = '12px Orbitron, monospace';
            this.ctx.textAlign = 'right';
            this.ctx.fillText('P2: Used', this.canvas.width - 10, 30);
        }
        
        // Draw speed multiplier indicator
        if (this.ball.speedMultiplier > 1) {
            this.ctx.fillStyle = '#FFD700';
            this.ctx.font = 'bold 14px Orbitron, monospace';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(`Speed: ${Math.round(this.ball.speedMultiplier * 100)}%`, this.canvas.width / 2, 30);
        }
        
        // Draw game state messages
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = 'bold 20px Orbitron, monospace';
        
        if (this.gameState === 'waiting') {
            this.ctx.fillText('Press SPACE to Start', this.canvas.width / 2, this.canvas.height / 2 + 50);
            this.ctx.font = '16px Orbitron, monospace';
            this.ctx.fillText('Arrow Keys (P1) | W/S (P2) | SPACE/SHIFT for Force Push', this.canvas.width / 2, this.canvas.height / 2 + 80);
        } else if (this.gameState === 'paused') {
            this.ctx.fillText('PAUSED - Press ESC to Resume', this.canvas.width / 2, this.canvas.height / 2);
        } else if (this.gameState === 'gameOver') {
            this.ctx.fillText(`Player ${this.winner} Wins!`, this.canvas.width / 2, this.canvas.height / 2);
            this.ctx.font = '16px Orbitron, monospace';
            this.ctx.fillText('Press SPACE to Play Again', this.canvas.width / 2, this.canvas.height / 2 + 30);
        }
        
        // Draw force push status
        if (this.forcePush.active) {
            this.ctx.fillStyle = '#FF00CC';
            this.ctx.font = 'bold 16px Orbitron, monospace';
            this.ctx.fillText('FORCE PUSH ACTIVE!', this.canvas.width / 2, this.canvas.height - 20);
        }
    }
    
    gameLoop() {
        if (!this.isRunning) return;
        
        this.update();
        this.render();
        
        this.animationId = requestAnimationFrame(() => this.gameLoop());
    }
    
    destroy() {
        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeyDown);
        document.removeEventListener('keyup', this.handleKeyUp);
    }
}

// ===== DEMO INITIALIZATION =====
let mainDemo = null;
let modalDemo = null;

function initializeDemo() {
    // Initialize main demo
    const mainCanvas = document.getElementById('demo-canvas');
    if (mainCanvas) {
        mainDemo = new PongDemo('demo-canvas');
    }
    
    // Initialize modal demo
    const modalCanvas = document.getElementById('modal-canvas');
    if (modalCanvas) {
        modalDemo = new PongDemo('modal-canvas');
    }
    
    // Setup demo start button
    const startDemoBtn = document.getElementById('start-demo');
    if (startDemoBtn) {
        startDemoBtn.addEventListener('click', () => {
            if (mainDemo) {
                mainDemo.startGame();
                document.getElementById('demo-overlay').style.display = 'none';
            }
        });
    }
}

function initializeModalDemo() {
    if (modalDemo) {
        modalDemo.resetGame();
        modalDemo.startGame();
    }
}

function stopModalDemo() {
    if (modalDemo) {
        modalDemo.destroy();
    }
}

// ===== AUTO-INITIALIZE =====
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeDemo, 100);
});

// ===== EXPORT FOR MODULE USAGE =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        PongDemo,
        initializeDemo,
        initializeModalDemo,
        stopModalDemo
    };
}
