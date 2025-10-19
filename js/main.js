// ===== MAIN JAVASCRIPT FOR PONG FORCE WEBSITE =====

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeWebsite();
});

// ===== INITIALIZATION =====
function initializeWebsite() {
    initializeAOS();
    initializeNavigation();
    initializeButtons();
    initializeScrollEffects();
    initializeModal();
    initializeParticles();
    initializeDownloadTracking();
}

// ===== AOS (Animate On Scroll) INITIALIZATION =====
function initializeAOS() {
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            easing: 'ease-in-out',
            once: true,
            offset: 100
        });
    }
}

// ===== NAVIGATION =====
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Navbar background on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(11, 12, 16, 0.98)';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 255, 255, 0.3)';
        } else {
            navbar.style.background = 'rgba(11, 12, 16, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });
}

// ===== BUTTON INTERACTIONS =====
function initializeButtons() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        // Add click sound effect
        button.addEventListener('click', function(e) {
            playClickSound();
            addButtonRipple(this, e);
        });
        
        // Add hover effects
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Special handling for demo button
    const tryDemoBtn = document.getElementById('try-demo-btn');
    if (tryDemoBtn) {
        tryDemoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openDemoModal();
        });
    }
    
    // Special handling for download button
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            trackDownload();
        });
    }
}

// ===== BUTTON RIPPLE EFFECT =====
function addButtonRipple(button, event) {
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    button.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// ===== SCROLL EFFECTS =====
function initializeScrollEffects() {
    const sections = document.querySelectorAll('section');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Special effects for specific sections
                if (entry.target.id === 'hero') {
                    animateHeroElements();
                } else if (entry.target.id === 'force-showcase') {
                    animateForceShowcase();
                } else if (entry.target.id === 'features') {
                    animateFeatureCards();
                }
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

// ===== HERO ANIMATIONS =====
function animateHeroElements() {
    const heroTitle = document.querySelector('.hero-title');
    const heroTagline = document.querySelector('.hero-tagline');
    const heroDescription = document.querySelector('.hero-description');
    const heroButtons = document.querySelector('.hero-buttons');
    
    if (heroTitle) {
        heroTitle.style.animation = 'fadeInUp 1s ease-out';
    }
    
    if (heroTagline) {
        setTimeout(() => {
            heroTagline.style.animation = 'fadeInUp 1s ease-out';
        }, 300);
    }
    
    if (heroDescription) {
        setTimeout(() => {
            heroDescription.style.animation = 'fadeInUp 1s ease-out';
        }, 600);
    }
    
    if (heroButtons) {
        setTimeout(() => {
            heroButtons.style.animation = 'fadeInUp 1s ease-out';
        }, 900);
    }
}

// ===== FORCE SHOWCASE ANIMATIONS =====
function animateForceShowcase() {
    const forceDemo = document.querySelector('.force-demo');
    const showcaseText = document.querySelector('.showcase-text');
    
    if (forceDemo) {
        forceDemo.style.animation = 'fadeInUp 1s ease-out';
    }
    
    if (showcaseText) {
        setTimeout(() => {
            showcaseText.style.animation = 'fadeInUp 1s ease-out';
        }, 300);
    }
}

// ===== FEATURE CARDS ANIMATIONS =====
function animateFeatureCards() {
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.animation = 'fadeInUp 0.8s ease-out';
        }, index * 200);
    });
}

// ===== MODAL FUNCTIONALITY =====
function initializeModal() {
    const modal = document.getElementById('demo-modal');
    const closeBtn = document.getElementById('close-demo');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeDemoModal);
    }
    
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeDemoModal();
            }
        });
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.style.display === 'block') {
            closeDemoModal();
        }
    });
}

function openDemoModal() {
    const modal = document.getElementById('demo-modal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Initialize demo game in modal
        setTimeout(() => {
            initializeModalDemo();
        }, 100);
    }
}

function closeDemoModal() {
    const modal = document.getElementById('demo-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Stop demo game
        stopModalDemo();
    }
}

// ===== PARTICLE SYSTEM =====
function initializeParticles() {
    const particlesContainer = document.getElementById('particles-container');
    if (!particlesContainer) return;
    
    const particleCount = 50;
    const particles = [];
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        createParticle(particlesContainer);
    }
    
    // Animate particles
    animateParticles();
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Random properties
    const size = Math.random() * 3 + 1;
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight;
    const color = Math.random() > 0.5 ? '#00FFFF' : '#FF00CC';
    const opacity = Math.random() * 0.5 + 0.2;
    
    particle.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        border-radius: 50%;
        left: ${x}px;
        top: ${y}px;
        opacity: ${opacity};
        box-shadow: 0 0 ${size * 2}px ${color};
        pointer-events: none;
    `;
    
    container.appendChild(particle);
    
    // Store particle data
    particle.data = {
        x: x,
        y: y,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: size,
        color: color
    };
}

function animateParticles() {
    const particles = document.querySelectorAll('.particle');
    
    particles.forEach(particle => {
        if (!particle.data) return;
        
        // Update position
        particle.data.x += particle.data.vx;
        particle.data.y += particle.data.vy;
        
        // Wrap around screen
        if (particle.data.x < 0) particle.data.x = window.innerWidth;
        if (particle.data.x > window.innerWidth) particle.data.x = 0;
        if (particle.data.y < 0) particle.data.y = window.innerHeight;
        if (particle.data.y > window.innerHeight) particle.data.y = 0;
        
        // Apply position
        particle.style.left = particle.data.x + 'px';
        particle.style.top = particle.data.y + 'px';
    });
    
    requestAnimationFrame(animateParticles);
}

// ===== SOUND EFFECTS =====
function playClickSound() {
    // Create audio context for sound effects
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(400, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    } catch (error) {
        console.log('Audio not supported');
    }
}

// ===== DOWNLOAD TRACKING =====
function initializeDownloadTracking() {
    // Track download button clicks
    const downloadButtons = document.querySelectorAll('[download]');
    downloadButtons.forEach(button => {
        button.addEventListener('click', trackDownload);
    });
}

function trackDownload() {
    // Analytics tracking (replace with your analytics code)
    console.log('Download initiated');
    
    // You can add Google Analytics or other tracking here
    if (typeof gtag !== 'undefined') {
        gtag('event', 'download', {
            'event_category': 'engagement',
            'event_label': 'PongForce.exe'
        });
    }
    
    // Show download confirmation
    showDownloadConfirmation();
    
    // Show download instructions
    showDownloadInstructions();
}

function showDownloadConfirmation() {
    // Create temporary notification
    const notification = document.createElement('div');
    notification.className = 'download-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">⬇️</span>
            <span class="notification-text">Download started!</span>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: rgba(0, 255, 255, 0.9);
        color: #0B0C10;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        z-index: 3000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function showDownloadInstructions() {
    // Show download instructions with animation
    const instructions = document.getElementById('download-instructions');
    if (instructions) {
        instructions.style.display = 'block';
        instructions.style.opacity = '0';
        instructions.style.transform = 'translateY(20px)';
        
        // Animate in
        setTimeout(() => {
            instructions.style.transition = 'all 0.5s ease-out';
            instructions.style.opacity = '1';
            instructions.style.transform = 'translateY(0)';
        }, 100);
    }
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== WINDOW RESIZE HANDLER =====
window.addEventListener('resize', debounce(function() {
    // Recalculate particle positions on resize
    const particles = document.querySelectorAll('.particle');
    particles.forEach(particle => {
        if (particle.data) {
            if (particle.data.x > window.innerWidth) {
                particle.data.x = window.innerWidth;
            }
            if (particle.data.y > window.innerHeight) {
                particle.data.y = window.innerHeight;
            }
        }
    });
}, 250));

// ===== PERFORMANCE OPTIMIZATION =====
// Use requestIdleCallback for non-critical animations
if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
        // Initialize non-critical features here
        initializeAdvancedAnimations();
    });
} else {
    setTimeout(initializeAdvancedAnimations, 100);
}

function initializeAdvancedAnimations() {
    // Add any advanced animations that aren't critical for initial load
    console.log('Advanced animations initialized');
}

// ===== ERROR HANDLING =====
window.addEventListener('error', function(e) {
    console.error('Website error:', e.error);
    // You can add error reporting here
});

// ===== EXPORT FOR MODULE USAGE =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeWebsite,
        openDemoModal,
        closeDemoModal,
        trackDownload
    };
}
