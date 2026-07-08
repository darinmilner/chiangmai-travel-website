// Mobile menu toggle with Alpine.js
document.addEventListener('alpine:init', () => {
    Alpine.data('mobileMenu', () => ({
        open: false,
        toggle() {
            this.open = !this.open;
        }
    }));
});

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Carousel auto-advance (optional)
// If you want the carousel to auto-advance, uncomment this:
/*
document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('[x-data*="currentSlide"]');
    carousels.forEach(carousel => {
        const data = Alpine.$data(carousel);
        if (data && data.next) {
            setInterval(() => {
                data.next();
            }, 5000);
        }
    });
});
*/