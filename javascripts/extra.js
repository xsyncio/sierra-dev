/*
   Neon Cyberpunk Interactive Effects - ENHANCED
   Author: Xsyncio
   Version: 3.0 - EXTREME CYBERPUNK EDITION
*/

document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 Sierra Dev: EXTREME CYBERPUNK MODE ACTIVATED");

    // ==========================================================================
    // 1. Dynamic Title Glitch Effect
    // ==========================================================================
    const title = document.querySelector(".md-header__title");
    if (title) {
        // Enhanced glitch with duration
        title.addEventListener("mouseover", () => {
            let glitchCount = 0;
            const glitchInterval = setInterval(() => {
                title.style.textShadow = `${Math.random() * 4 - 2}px 0 var(--neon-pink), ${Math.random() * 4 - 2}px 0 var(--neon-cyan)`;
                glitchCount++;
                if (glitchCount > 5) {
                    clearInterval(glitchInterval);
                    title.style.textShadow = "0 0 10px rgba(0, 243, 255, 0.5), 0 0 20px rgba(188, 19, 254, 0.3)";
                }
            }, 50);
        });
    }

    // ==========================================================================
    // 2. Smooth Scroll with Neon Progress Bar
    // ==========================================================================
    const progressBar = document.createElement("div");
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan));
        z-index: 9999;
        width: 0%;
        transition: width 0.1s ease;
        box-shadow: 0 0 10px var(--neon-cyan), 0 0 20px var(--neon-purple);
    `;
    document.body.appendChild(progressBar);

    window.addEventListener("scroll", () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        progressBar.style.width = scrolled + "%";
    });

    // ==========================================================================
    // 3. Interactive Code Blocks with Enhanced Glow
    // ==========================================================================
    const codeBlocks = document.querySelectorAll("pre");
    codeBlocks.forEach(block => {
        // Add data attribute for tracking
        block.setAttribute('data-code-block', 'true');

        block.addEventListener("mouseenter", () => {
            block.style.borderColor = "var(--neon-cyan)";
            block.style.boxShadow = "0 0 30px rgba(0, 243, 255, 0.3), 0 0 60px rgba(188, 19, 254, 0.2)";
            block.style.transform = "scale(1.01)";
            block.style.transition = "all 0.3s ease";
        });

        block.addEventListener("mouseleave", () => {
            block.style.borderColor = "rgba(0, 243, 255, 0.2)";
            block.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.3), inset 0 0 20px rgba(0, 243, 255, 0.05)";
            block.style.transform = "scale(1)";
        });
    });

    // ==========================================================================
    // 4. Enhanced Copy Button Feedback
    // ==========================================================================
    // Intercept copy events for better feedback
    document.addEventListener('copy', (e) => {
        const selection = window.getSelection().toString();
        if (selection.length > 10) { // Only for meaningful copies
            showNotification('📋 Code copied! Ready to paste.', 'success');
        }
    });

    // ==========================================================================
    // 5. Particle System Background
    // ==========================================================================
    function createParticleSystem() {
        const canvas = document.createElement('canvas');
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0.3;
        `;
        document.body.appendChild(canvas);

        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const particles = [];
        const particleCount = 50;

        // Create particles
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 2 + 1,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                color: ['#00f3ff', '#bc13fe', '#0aff00'][Math.floor(Math.random() * 3)]
            });
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach(p => {
                // Move
                p.x += p.vx;
                p.y += p.vy;

                // Bounce
                if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
                if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

                // Draw
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();

                // Glow
                ctx.shadowBlur = 10;
                ctx.shadowColor = p.color;
            });

            requestAnimationFrame(animate);
        }

        animate();

        // Resize handler
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    }

    // Initialize particle system
    createParticleSystem();

    // ==========================================================================
    // 6. Notification System
    // ==========================================================================
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${type === 'success' ? 'rgba(10, 255, 0, 0.1)' : 'rgba(0, 243, 255, 0.1)'};
            border: 1px solid ${type === 'success' ? 'var(--neon-green)' : 'var(--neon-cyan)'};
            color: ${type === 'success' ? 'var(--neon-green)' : 'var(--neon-cyan)'};
            padding: 12px 20px;
            border-radius: 4px;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
            box-shadow: 0 0 20px ${type === 'success' ? 'rgba(10, 255, 0, 0.3)' : 'rgba(0, 243, 255, 0.3)'};
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    // ==========================================================================
    // 7. Enhanced Typing Effect for Hero Text
    // ==========================================================================
    const heroText = document.querySelector(".cyber-hero-text");
    if (heroText) {
        const text = heroText.textContent;
        heroText.textContent = "";
        heroText.style.borderRight = "2px solid var(--neon-cyan)";
        let i = 0;

        function typeWriter() {
            if (i < text.length) {
                heroText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 30);
            } else {
                // Remove cursor after typing
                setTimeout(() => {
                    heroText.style.borderRight = "none";
                }, 500);
            }
        }

        // Start typing after small delay
        setTimeout(typeWriter, 500);
    }

    // ==========================================================================
    // 8. Interactive Table Row Highlight
    // ==========================================================================
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function () {
                this.style.background = 'rgba(0, 243, 255, 0.05)';
                this.style.transform = 'translateX(4px)';
                this.style.transition = 'all 0.2s ease';
            });
            row.addEventListener('mouseleave', function () {
                this.style.background = '';
                this.style.transform = '';
            });
        });
    });

    // ==========================================================================
    // 9. Add Animation Styles
    // ==========================================================================
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // ==========================================================================
    // 10. Easter Egg: Konami Code
    // ==========================================================================
    let konamiCode = [];
    const konamiPattern = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

    document.addEventListener('keydown', (e) => {
        konamiCode.push(e.key);
        konamiCode = konamiCode.slice(-10);

        if (konamiCode.join('') === konamiPattern.join('')) {
            showNotification('🎮 MATRIX MODE ACTIVATED!', 'success');
            // Add extra cool effect
            document.body.style.animation = 'pulse 0.5s ease';
            setTimeout(() => {
                document.body.style.animation = '';
            }, 500);
        }
    });

    console.log("✨ All cyberpunk enhancements loaded!");
});


document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 Sierra Dev: Cyberpunk Theme Loaded");

    // ==========================================================================
    // 1. Dynamic Title Glitch Effect
    // ==========================================================================
    const title = document.querySelector(".md-header__title");
    if (title) {
        title.addEventListener("mouseover", () => {
            title.style.textShadow = "2px 0 var(--neon-pink), -2px 0 var(--neon-cyan)";
            setTimeout(() => {
                title.style.textShadow = "0 0 10px rgba(0, 243, 255, 0.5)";
            }, 200);
        });
    }

    // ==========================================================================
    // 2. Smooth Scroll with Neon Trace
    // ==========================================================================
    // Add a subtle progress bar at the top
    const progressBar = document.createElement("div");
    progressBar.style.position = "fixed";
    progressBar.style.top = "0";
    progressBar.style.left = "0";
    progressBar.style.height = "2px";
    progressBar.style.background = "linear-gradient(90deg, var(--neon-purple), var(--neon-cyan))";
    progressBar.style.zIndex = "9999";
    progressBar.style.width = "0%";
    progressBar.style.transition = "width 0.1s ease";
    progressBar.style.boxShadow = "0 0 10px var(--neon-cyan)";
    document.body.appendChild(progressBar);

    window.addEventListener("scroll", () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        progressBar.style.width = scrolled + "%";
    });

    // ==========================================================================
    // 3. Interactive Code Blocks (Copy Button Glow)
    // ==========================================================================
    const codeBlocks = document.querySelectorAll("pre");
    codeBlocks.forEach(block => {
        block.addEventListener("mouseenter", () => {
            block.style.borderColor = "var(--neon-cyan)";
            block.style.boxShadow = "0 0 20px rgba(0, 243, 255, 0.1)";
        });
        block.addEventListener("mouseleave", () => {
            block.style.borderColor = "rgba(255, 255, 255, 0.1)";
            block.style.boxShadow = "0 4px 20px rgba(0, 0, 0, 0.3)";
        });
    });

    // ==========================================================================
    // 4. Theme Toggle Sound Effect (Optional - kept subtle)
    // ==========================================================================
    // Note: Audio requires user interaction first, so we skip actual audio for now
    // to avoid annoyance, but we add a visual flash.

    const themeToggle = document.querySelector(".md-header__option[data-md-component='palette']");
    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            // Flash effect on screen
            const flash = document.createElement("div");
            flash.style.position = "fixed";
            flash.style.top = "0";
            flash.style.left = "0";
            flash.style.width = "100vw";
            flash.style.height = "100vh";
            flash.style.background = "white";
            flash.style.opacity = "0.1";
            flash.style.pointerEvents = "none";
            flash.style.zIndex = "99999";
            flash.style.transition = "opacity 0.3s ease";
            document.body.appendChild(flash);

            setTimeout(() => {
                flash.style.opacity = "0";
                setTimeout(() => flash.remove(), 300);
            }, 50);
        });
    }

    // ==========================================================================
    // 5. Typing Effect for Hero Text (if present)
    // ==========================================================================
    // Looks for an element with class 'cyber-hero-text'
    const heroText = document.querySelector(".cyber-hero-text");
    if (heroText) {
        const text = heroText.textContent;
        heroText.textContent = "";
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                heroText.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        }
        typeWriter();
    }
});