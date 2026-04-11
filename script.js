// ============================================
// ANIMATION MANAGER
// ============================================

class TypingAnimation {
    constructor(elementId, phrases, options = {}) {
        this.element = document.getElementById(elementId);
        this.phrases = phrases;
        this.currentPhraseIndex = 0;
        this.currentCharIndex = 0;
        this.isDeleting = false;
        this.typingSpeed = options.typingSpeed || 70;
        this.deletingSpeed = options.deletingSpeed || 40;
        this.pauseTime = options.pauseTime || 2500;
        this.isRunning = false;
    }

    start() {
        this.isRunning = true;
        this.type();
    }

    type() {
        if (!this.isRunning) return;

        const currentPhrase = this.phrases[this.currentPhraseIndex];

        if (!this.isDeleting) {
            this.typeCharacter(currentPhrase);
        } else {
            this.deleteCharacter(currentPhrase);
        }
    }

    typeCharacter(phrase) {
        if (this.currentCharIndex < phrase.length) {
            this.element.textContent = phrase.substring(0, this.currentCharIndex + 1);
            this.currentCharIndex++;
            setTimeout(() => this.type(), this.typingSpeed);
        } else {
            // Pause before deleting
            setTimeout(() => {
                this.isDeleting = true;
                this.type();
            }, this.pauseTime);
        }
    }

    deleteCharacter(phrase) {
        if (this.currentCharIndex > 0) {
            this.element.textContent = phrase.substring(0, this.currentCharIndex - 1);
            this.currentCharIndex--;
            setTimeout(() => this.type(), this.deletingSpeed);
        } else {
            // Move to next phrase
            this.isDeleting = false;
            this.currentPhraseIndex = (this.currentPhraseIndex + 1) % this.phrases.length;
            setTimeout(() => this.type(), 300);
        }
    }

    stop() {
        this.isRunning = false;
    }
}

// ============================================
// NAVIGATION MANAGER
// ============================================

class Navigation {
    constructor() {
        this.navLinks = document.querySelectorAll('nav a[href^="#"]');
        this.init();
    }

    init() {
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handleNavClick(e));
        });
    }

    handleNavClick(e) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href');
        const target = document.querySelector(targetId);

        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
}

// ============================================
// SCROLL REVEAL ANIMATION
// ============================================

class ScrollReveal {
    constructor() {
        this.elements = document.querySelectorAll('[data-reveal]');
        this.observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        this.init();
    }

    init() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.revealElement(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, this.observerOptions);

            this.elements.forEach(element => observer.observe(element));
        }
    }

    revealElement(element) {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
        element.classList.add('revealed');
    }
}

// ============================================
// APP INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize typing animation
    const typingPhrases = [
        'Strona dla fryzjera w 5min',
        'Strona dla mechanika w 5min',
        'Strona dla restauracji w 5min',
        'Strona dla dentysty w 5min',
        'Strona dla fotografa w 5min',
        'Strona dla salonu kosmetyki w 5min',
        'Strona dla doradcy finansowego w 5min',
        'Strona dla trenera fitness w 5min',
        'Strona dla agenta nieruchomości w 5min',
        'Strona dla elektryka w 5min'
    ];

    const typing = new TypingAnimation('typingText', typingPhrases);
    typing.start();

    // Initialize navigation
    new Navigation();

    // Initialize scroll reveal
    new ScrollReveal();

    // Button listeners
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // Smooth interaction
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = '';
            }, 150);
        });
    });
});
