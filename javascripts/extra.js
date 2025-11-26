/*
   Neon Cyberpunk Interactive Effects
   Author: Xsyncio (via Antigravity)
   Version: 2.0
*/

document.addEventListener("DOMContentLoaded", function () {
    console.log("🚀 Sierra SDK: Cyberpunk Theme Loaded");

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