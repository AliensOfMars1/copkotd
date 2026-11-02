// ============================================
// MAIN JAVASCRIPT - The Church of Pentecost KOTD
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // STICKY NAVBAR - Changes background on scroll
    // ============================================
    const navbar = document.getElementById('navbar');
    const hamburger = document.getElementById('hamburger');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    const mobileMenuClose = document.getElementById('mobile-menu-close');
    
    // Handle scroll event for navbar styling
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // ============================================
    // MOBILE MENU TOGGLE (Works on all devices)
    // ============================================
    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        mobileMenuOverlay.classList.toggle('active');
        
        // Prevent body scroll when menu is open
        if (mobileMenuOverlay.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    });
    
    // Close mobile menu when clicking close button
    mobileMenuClose.addEventListener('click', function() {
        closeMenu();
    });
    
    // Close mobile menu when clicking overlay background
    mobileMenuOverlay.addEventListener('click', function(event) {
        if (event.target === mobileMenuOverlay) {
            closeMenu();
        }
    });
    
    // Close mobile menu when clicking a link
    const mobileMenuLinks = document.querySelectorAll('.mobile-menu-list a, .mobile-menu-legal a');
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', function() {
            closeMenu();
        });
    });
    
    // Close mobile menu on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && mobileMenuOverlay.classList.contains('active')) {
            closeMenu();
        }
    });
    
    function closeMenu() {
        hamburger.classList.remove('active');
        mobileMenuOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    // ============================================
    // SCROLL ANIMATIONS - Fade in elements on scroll
    // ============================================
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    fadeElements.forEach(element => {
        fadeInObserver.observe(element);
    });
    
    // ============================================
    // SMOOTH SCROLL FOR ANCHOR LINKS
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    console.log('The Church of Pentecost KOTD - Website Loaded Successfully');
});


// ============================================
// HERO IMAGE CARD SLIDER
// ============================================
function initHeroSlider() {
    const slides = document.querySelectorAll('.hero-card-slide');
    const dots = document.querySelectorAll('.hero-dot');
    const prevBtn = document.getElementById('hero-prev');
    const nextBtn = document.getElementById('hero-next');
    
    if (!slides.length) return;
    
    let currentSlide = 0;
    let slideInterval;
    const autoPlayDelay = 5000; // Change image every 5 seconds
    
    // Show specific slide
    function showSlide(index) {
        // Remove active class from all slides and dots
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        // Add active class to current slide and dot
        slides[index].classList.add('active');
        dots[index].classList.add('active');
        currentSlide = index;
    }
    
    // Next slide
    function nextSlide() {
        const next = (currentSlide + 1) % slides.length;
        showSlide(next);
    }
    
    // Previous slide
    function prevSlide() {
        const prev = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(prev);
    }
    
    // Start auto-play
    function startAutoPlay() {
        stopAutoPlay();
        slideInterval = setInterval(nextSlide, autoPlayDelay);
    }
    
    // Stop auto-play
    function stopAutoPlay() {
        if (slideInterval) {
            clearInterval(slideInterval);
        }
    }
    
    // Event Listeners
    if (prevBtn) {
        prevBtn.addEventListener('click', (e) => {
            e.preventDefault();
            prevSlide();
            startAutoPlay(); // Reset timer
        });
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', (e) => {
            e.preventDefault();
            nextSlide();
            startAutoPlay(); // Reset timer
        });
    }
    
    // Dot navigation
    dots.forEach(dot => {
        dot.addEventListener('click', function() {
            const slideIndex = parseInt(this.getAttribute('data-slide'));
            showSlide(slideIndex);
            startAutoPlay(); // Reset timer
        });
    });
    
    // Pause on hover
    const cardContainer = document.querySelector('.hero-card-container');
    if (cardContainer) {
        cardContainer.addEventListener('mouseenter', stopAutoPlay);
        cardContainer.addEventListener('mouseleave', startAutoPlay);
    }
    
    // Touch swipe support
    let touchStartX = 0;
    let touchEndX = 0;
    
    if (cardContainer) {
        cardContainer.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });
        
        cardContainer.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        });
    }
    
    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
            // Swipe left - next slide
            nextSlide();
            startAutoPlay();
        }
        if (touchEndX > touchStartX + swipeThreshold) {
            // Swipe right - previous slide
            prevSlide();
            startAutoPlay();
        }
    }
    
    // Initialize
    showSlide(0);
    startAutoPlay();
    
    console.log('Hero Card Slider Initialized');
}

// Add to DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...
    
    // Initialize hero slider
    initHeroSlider();
});