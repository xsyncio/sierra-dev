// Sierra Dev - Custom JavaScript Enhancements
document.addEventListener("DOMContentLoaded", function() {
    
    // Add glowing effect to code blocks on hover
    const codeBlocks = document.querySelectorAll('.highlight');
    codeBlocks.forEach(block => {
        block.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 25px rgba(0, 255, 0, 0.3)';
            this.style.transform = 'translateY(-2px)';
        });
        
        block.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 4px 20px rgba(0, 255, 0, 0.1)';
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add typing effect to the main heading (if it exists)
    const mainHeading = document.querySelector('h1');
    if (mainHeading) {
        const originalText = mainHeading.textContent;
        let index = 0;
        mainHeading.textContent = '';
        
        function typeWriter() {
            if (index < originalText.length) {
                mainHeading.textContent += originalText.charAt(index);
                index++;
                setTimeout(typeWriter, 50);
            }
        }
        
        // Start typing effect after a short delay
        setTimeout(typeWriter, 500);
    }
    
    // Add smooth reveal animation for sections
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Apply animation to all content sections
    const sections = document.querySelectorAll('article > *');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(section);
    });
    
    // Enhanced search functionality
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 20px rgba(0, 255, 0, 0.3)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.style.boxShadow = '0 0 15px rgba(255, 0, 0, 0.3)';
        });
    }
    
    // Add interactive elements to navigation
    const navLinks = document.querySelectorAll('.md-nav__link');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.textShadow = '0 0 10px currentColor';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.textShadow = 'none';
        });
    });
    
    // Add particle effect to header (optional - lightweight version)
    function createParticle() {
        const header = document.querySelector('.md-header');
        if (!header) return;
        
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '2px';
        particle.style.height = '2px';
        particle.style.backgroundColor = Math.random() > 0.5 ? '#ff0000' : '#00ff00';
        particle.style.borderRadius = '50%';
        particle.style.pointerEvents = 'none';
        particle.style.opacity = '0.7';
        particle.style.left = Math.random() * window.innerWidth + 'px';
        particle.style.top = '0px';
        particle.style.zIndex = '1';
        
        header.appendChild(particle);
        
        let pos = 0;
        const animation = setInterval(() => {
            pos += 2;
            particle.style.top = pos + 'px';
            particle.style.opacity = (1 - pos / 100).toString();
            
            if (pos > 100) {
                clearInterval(animation);
                particle.remove();
            }
        }, 50);
    }
    
    // Create particles occasionally
    setInterval(createParticle, 2000);
    
    console.log('🚀 Sierra Dev Documentation Enhanced - Pure Black Theme Activated!');
});