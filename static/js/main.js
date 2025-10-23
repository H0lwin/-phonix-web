/**
 * ================================================================
 * PHONIX - Main JavaScript Application
 * Professional Legal Services Platform
 * ================================================================
 */

// ================================================================
// CONFIGURATION & CONSTANTS
// ================================================================
const CONFIG = {
    scrollBehavior: 'smooth',
    animationDuration: 300,
    statAnimationDuration: 2000,
    debounceDelay: 250,
};

// ================================================================
// APPLICATION STATE
// ================================================================
const AppState = {
    isLoaded: false,
    isAnimating: false,
    statsAnimated: false,
    formSubmitted: false,
};

// ================================================================
// INITIALIZATION
// ================================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Phonix Application Starting...');
    
    AppState.isLoaded = true;
    
    initializeApp();
    setupEventListeners();
    setupIntersectionObserver();
});

window.addEventListener('load', function() {
    console.log('✅ Phonix Application Fully Loaded');
    // Trigger animations that depend on full load
    initializeScrollAnimations();
});

// ================================================================
// MAIN INITIALIZATION
// ================================================================
function initializeApp() {
    console.log('🔧 Initializing Phonix Application');
    
    // Setup smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ================================================================
// EVENT LISTENERS
// ================================================================
function setupEventListeners() {
    console.log('👂 Setting up Event Listeners');
    
    // Navbar scroll effects
    window.addEventListener('scroll', debounce(handleScroll, CONFIG.debounceDelay));
    
    // Form submission
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Button click handlers
    document.querySelectorAll('[data-service]').forEach(el => {
        el.addEventListener('click', handleServiceClick);
    });
    
    document.querySelectorAll('[data-feature]').forEach(el => {
        el.addEventListener('click', handleFeatureClick);
    });
}

// ================================================================
// SCROLL HANDLER
// ================================================================
function handleScroll() {
    const navbar = document.querySelector('.navbar');
    const scrolled = window.scrollY > 50;
    
    if (scrolled) {
        navbar?.classList.add('scrolled');
    } else {
        navbar?.classList.remove('scrolled');
    }
    
    // Update active nav link
    updateActiveNavLink();
}

// ================================================================
// INTERSECTION OBSERVER - For animations on scroll
// ================================================================
function setupIntersectionObserver() {
    console.log('👀 Setting up Intersection Observer');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Trigger animation
                entry.target.classList.add('animate-in');
                
                // Special handling for stats section
                if (entry.target.classList.contains('stats')) {
                    if (!AppState.statsAnimated) {
                        animateStats();
                        AppState.statsAnimated = true;
                    }
                }
            }
        });
    }, observerOptions);
    
    // Observe all animated elements
    document.querySelectorAll('.service-card, .feature-item, .testimonial-card, .team-member, .dashboard-card, .stats').forEach(el => {
        observer.observe(el);
    });
}

// ================================================================
// SCROLL ANIMATIONS
// ================================================================
function initializeScrollAnimations() {
    console.log('✨ Initializing Scroll Animations');
    
    const cards = document.querySelectorAll('.service-card, .feature-item, .testimonial-card, .team-member, .dashboard-card');
    
    cards.forEach((card, index) => {
        card.style.animation = `fadeIn ${CONFIG.animationDuration}ms ease-in forwards`;
        card.style.animationDelay = `${index * 50}ms`;
    });
}

// ================================================================
// STATS ANIMATION
// ================================================================
function animateStats() {
    console.log('📊 Animating Stats');
    
    const statElements = document.querySelectorAll('.hero-stat strong');
    
    statElements.forEach(el => {
        const target = parseInt(el.textContent.replace(/\D/g, ''));
        const text = el.textContent;
        
        let current = 0;
        const increment = Math.ceil(target / (CONFIG.statAnimationDuration / 16));
        
        const counter = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(counter);
            }
            el.textContent = current + (text.includes('+') ? '+' : '');
        }, 16);
    });
}

// ================================================================
// FORM HANDLING
// ================================================================
function handleFormSubmit(e) {
    e.preventDefault();
    console.log('📝 Form Submitted');
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span>⏳</span> در حال ارسال...';
    submitBtn.disabled = true;
    
    // Simulate form submission
    setTimeout(() => {
        // Show success message
        showNotification('✅ پیام شما با موفقیت ارسال شد!', 'success');
        
        // Reset form
        form.reset();
        
        // Restore button
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        
        AppState.formSubmitted = true;
    }, 1000);
}

// ================================================================
// SERVICE CLICK HANDLER
// ================================================================
function handleServiceClick(e) {
    console.log('📋 Service Clicked:', e.target.closest('.service-card'));
    // Could add more interactivity here
}

// ================================================================
// FEATURE CLICK HANDLER
// ================================================================
function handleFeatureClick(e) {
    console.log('⭐ Feature Clicked:', e.target.closest('.feature-item'));
    // Could add more interactivity here
}

// ================================================================
// ACTIVE NAV LINK
// ================================================================
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a');
    
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        if (window.pageYOffset >= sectionTop - 100) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// ================================================================
// NOTIFICATION SYSTEM
// ================================================================
function showNotification(message, type = 'info') {
    console.log(`📢 Notification [${type}]:`, message);
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        animation: slideInRight 0.3s ease-in-out;
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideInLeft 0.3s ease-in-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ================================================================
// UTILITY FUNCTIONS
// ================================================================

/**
 * Debounce function to limit function calls
 */
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

/**
 * Get CSRF token from meta tag
 */
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

/**
 * Fetch API wrapper with error handling
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                ...options.headers,
            }
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('❌ API Error:', error);
        throw error;
    }
}

/**
 * Add ripple effect to buttons
 */
function addRippleEffect(event) {
    const button = event.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = diameter + 'px';
    circle.style.left = event.clientX - button.offsetLeft - radius + 'px';
    circle.style.top = event.clientY - button.offsetTop - radius + 'px';
    circle.classList.add('ripple');
    
    const ripple = button.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }
    
    button.appendChild(circle);
}

// ================================================================
// SCROLL TO ELEMENT
// ================================================================
function scrollToElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// ================================================================
// CHECK IF ELEMENT IS IN VIEWPORT
// ================================================================
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.bottom >= 0
    );
}

// ================================================================
// PHONIX APP GLOBAL OBJECT
// ================================================================
window.PhonixApp = {
    state: AppState,
    config: CONFIG,
    showNotification,
    scrollToElement,
    isInViewport,
    fetchAPI,
    getCsrfToken,
    handleFormSubmit,
    animateStats,
};

console.log('✨ Phonix App Loaded. Access methods via window.PhonixApp');