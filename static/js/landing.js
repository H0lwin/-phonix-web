// // Landing Page JavaScript

// document.addEventListener('DOMContentLoaded', function() {
//     // Smooth scroll for anchor links
//     const anchors = document.querySelectorAll('a[href^="#"]');
//     anchors.forEach(anchor => {
//         anchor.addEventListener('click', function(e) {
//             const href = this.getAttribute('href');
//             if (href === '#') return;
            
//             const target = document.querySelector(href);
//             if (target) {
//                 e.preventDefault();
//                 target.scrollIntoView({
//                     behavior: 'smooth',
//                     block: 'start'
//                 });
//             }
//         });
//     });

//     // Contact form handling
//     const contactForm = document.getElementById('contactForm');
//     if (contactForm) {
//         contactForm.addEventListener('submit', function(e) {
//             e.preventDefault();
            
//             // Get form data
//             const formData = new FormData(this);
            
//             // Show success message
//             showNotification('پیام شما با موفقیت ارسال شد!', 'success');
            
//             // Reset form
//             this.reset();
//         });
//     }

//     // Navbar scroll effect
//     const navbar = document.querySelector('.navbar');
//     window.addEventListener('scroll', function() {
//         if (window.scrollY > 100) {
//             navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
//         } else {
//             navbar.style.boxShadow = 'var(--shadow)';
//         }
//     });

//     // Animation on scroll
//     const observerOptions = {
//         threshold: 0.1,
//         rootMargin: '0px 0px -50px 0px'
//     };

//     const observer = new IntersectionObserver(function(entries) {
//         entries.forEach(entry => {
//             if (entry.isIntersecting) {
//                 entry.target.style.opacity = '1';
//                 entry.target.style.transform = 'translateY(0)';
//             }
//         });
//     }, observerOptions);

//     document.querySelectorAll('.service-card, .feature-item, .team-member').forEach(el => {
//         el.style.opacity = '0';
//         el.style.transform = 'translateY(20px)';
//         el.style.transition = 'all 0.6s ease-out';
//         observer.observe(el);
//     });
// });

// // Show notification
// function showNotification(message, type = 'info') {
//     const notification = document.createElement('div');
//     notification.className = `notification notification-${type}`;
//     notification.textContent = message;
    
//     const style = document.createElement('style');
//     style.textContent = `
//         .notification {
//             position: fixed;
//             top: 20px;
//             right: 20px;
//             padding: 1rem 1.5rem;
//             border-radius: 0.5rem;
//             background-color: #fff;
//             box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
//             z-index: 9999;
//             animation: slideIn 0.3s ease-out;
//         }
        
//         @keyframes slideIn {
//             from {
//                 transform: translateX(400px);
//                 opacity: 0;
//             }
//             to {
//                 transform: translateX(0);
//                 opacity: 1;
//             }
//         }
        
//         .notification-success {
//             border-right: 4px solid #48bb78;
//             color: #22543d;
//         }
        
//         .notification-error {
//             border-right: 4px solid #f56565;
//             color: #742a2a;
//         }
        
//         .notification-info {
//             border-right: 4px solid #667eea;
//             color: #3c366b;
//         }
        
//         .notification-warning {
//             border-right: 4px solid #ed8936;
//             color: #7c2d12;
//         }
//     `;
    
//     document.head.appendChild(style);
//     document.body.appendChild(notification);
    
//     setTimeout(() => {
//         notification.style.animation = 'slideOut 0.3s ease-out forwards';
//         setTimeout(() => notification.remove(), 300);
//     }, 3000);
// }

// // Add CSS animation
// const style = document.createElement('style');
// style.textContent = `
//     @keyframes slideOut {
//         from {
//             transform: translateX(0);
//             opacity: 1;
//         }
//         to {
//             transform: translateX(400px);
//             opacity: 0;
//         }
//     }
// `;
// document.head.appendChild(style);