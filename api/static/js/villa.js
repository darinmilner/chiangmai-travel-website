// Villa Gallery and Carousel functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get the images data from the data attribute
    const galleryContainer = document.getElementById('villa-gallery');
    if (!galleryContainer) return;

    let images = [];
    try {
        images = JSON.parse(galleryContainer.dataset.images || '[]');
    } catch (e) {
        console.error('Error parsing images data:', e);
        return;
    }

    if (images.length === 0) {
        galleryContainer.innerHTML = '<p class="text-center text-charcoal">No images available</p>';
        return;
    }

    // ===== CAROUSEL FUNCTIONALITY =====
    let currentSlide = 0;
    let timer = null;
    let isTransitioning = false;
    const slides = images;

    function startTimer() {
        if (timer) clearInterval(timer);
        timer = setInterval(() => {
            if (!isTransitioning) {
                nextSlide();
            }
        }, 5000);
    }

    function stopTimer() {
        clearInterval(timer);
    }

    function nextSlide() {
        if (isTransitioning) return;
        isTransitioning = true;
        currentSlide = (currentSlide + 1) % slides.length;
        updateCarousel();
        setTimeout(() => {
            isTransitioning = false;
        }, 600);
    }

    function prevSlide() {
        if (isTransitioning) return;
        isTransitioning = true;
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        updateCarousel();
        setTimeout(() => {
            isTransitioning = false;
        }, 600);
    }

    function goToSlide(index) {
        if (isTransitioning || index === currentSlide) return;
        isTransitioning = true;
        currentSlide = index;
        stopTimer();
        updateCarousel();
        setTimeout(() => {
            isTransitioning = false;
            startTimer();
        }, 600);
    }

    function updateCarousel() {
        const slidesWrapper = document.querySelector('.carousel-slides-wrapper');
        if (!slidesWrapper) return;

        // Use requestAnimationFrame for smooth animations
        requestAnimationFrame(() => {
            const slideWidth = 100 / slides.length;
            slidesWrapper.style.transform = `translateX(-${currentSlide * slideWidth}%)`;
        });

        // Update counter
        const counter = document.getElementById('carousel-counter');
        if (counter) {
            counter.textContent = `${currentSlide + 1} / ${slides.length}`;
        }

        // Update dots
        const dots = document.querySelectorAll('.carousel-dot');
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.add('active');
                dot.style.backgroundColor = '#1b5e20';
            } else {
                dot.classList.remove('active');
                dot.style.backgroundColor = '#d1d5db';
            }
        });
    }

    // Initialize carousel
    function initCarousel() {
        const carouselContainer = document.querySelector('.carousel-container');
        if (!carouselContainer) return;

        const slidesWrapper = carouselContainer.querySelector('.carousel-slides-wrapper');
        if (!slidesWrapper) return;

        // Clear existing content
        slidesWrapper.innerHTML = '';

        // Set up the wrapper for horizontal sliding
        slidesWrapper.style.cssText = `
            display: flex;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            width: ${slides.length * 100}%;
            height: 100%;
            will-change: transform;
        `;

        // Create slides with lazy loading
        const fragment = document.createDocumentFragment();

        slides.forEach((src, index) => {
            const div = document.createElement('div');
            div.className = 'carousel-slide';
            div.style.cssText = `
                flex: 0 0 ${100 / slides.length}%;
                height: 100%;
                position: relative;
                overflow: hidden;
                background: #f0f0f0;
            `;

            const img = document.createElement('img');
            // Use lazy loading
            if (index === 0) {
                img.src = src;
            } else {
                img.loading = 'lazy';
                img.dataset.src = src;
                // Load image when it's about to become visible
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const imgEl = entry.target;
                            imgEl.src = imgEl.dataset.src;
                            imgEl.removeAttribute('data-src');
                            observer.unobserve(imgEl);
                        }
                    });
                }, { rootMargin: '100px' });
                observer.observe(img);
            }

            img.className = 'w-full h-full object-cover';
            img.alt = `Villa photo ${index + 1}`;
            img.style.cssText = `
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
                background: #f0f0f0;
            `;

            div.appendChild(img);
            fragment.appendChild(div);
        });

        slidesWrapper.appendChild(fragment);

        // Set up navigation buttons with debouncing
        const prevBtn = carouselContainer.querySelector('.carousel-prev');
        const nextBtn = carouselContainer.querySelector('.carousel-next');

        let buttonTimeout = null;
        const debounceClick = (fn) => {
            return function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (buttonTimeout) return;
                buttonTimeout = setTimeout(() => {
                    buttonTimeout = null;
                }, 300);
                fn();
            };
        };

        if (prevBtn) {
            prevBtn.addEventListener('click', debounceClick(() => {
                stopTimer();
                prevSlide();
                setTimeout(startTimer, 600);
            }));
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', debounceClick(() => {
                stopTimer();
                nextSlide();
                setTimeout(startTimer, 600);
            }));
        }

        // Pause on hover - using passive event listeners
        const carouselWrapper = carouselContainer.querySelector('.carousel-wrapper');
        if (carouselWrapper) {
            carouselWrapper.addEventListener('mouseenter', stopTimer, { passive: true });
            carouselWrapper.addEventListener('mouseleave', startTimer, { passive: true });
        }

        // Update counter
        const counter = document.getElementById('carousel-counter');
        if (counter) {
            counter.textContent = `1 / ${slides.length}`;
        }

        // Build dots
        const dotsContainer = document.querySelector('.carousel-dots');
        if (dotsContainer) {
            dotsContainer.innerHTML = '';
            const dotsFragment = document.createDocumentFragment();

            slides.forEach((_, index) => {
                const dot = document.createElement('button');
                dot.className = `carousel-dot ${index === 0 ? 'active' : ''}`;
                dot.style.cssText = `
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    border: none;
                    padding: 0;
                    margin: 0 4px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    background-color: ${index === 0 ? '#1b5e20' : '#d1d5db'};
                `;
                dot.setAttribute('aria-label', `Go to slide ${index + 1}`);

                dot.addEventListener('click', () => {
                    if (index !== currentSlide) {
                        goToSlide(index);
                    }
                });

                dotsFragment.appendChild(dot);
            });

            dotsContainer.appendChild(dotsFragment);
        }

        // Start the timer
        startTimer();
    }

    // ===== LIGHTBOX FUNCTIONALITY =====
    let lightboxOpen = false;
    let lightboxCurrent = 0;

    function openLightbox(index) {
        lightboxOpen = true;
        lightboxCurrent = index;
        updateLightbox();
        const overlay = document.getElementById('lightbox-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            // Trigger reflow for smooth animation
            overlay.offsetHeight;
        }
    }

    function closeLightbox() {
        lightboxOpen = false;
        const overlay = document.getElementById('lightbox-overlay');
        if (overlay) {
            overlay.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    function navigateLightbox(direction) {
        lightboxCurrent = (lightboxCurrent + direction + slides.length) % slides.length;
        updateLightbox();
    }

    function updateLightbox() {
        const img = document.getElementById('lightbox-image');
        if (img) {
            // Preload next and previous images
            const nextIndex = (lightboxCurrent + 1) % slides.length;
            const prevIndex = (lightboxCurrent - 1 + slides.length) % slides.length;

            const preloadNext = new Image();
            preloadNext.src = slides[nextIndex];
            const preloadPrev = new Image();
            preloadPrev.src = slides[prevIndex];

            img.src = slides[lightboxCurrent];
            img.alt = `Villa photo ${lightboxCurrent + 1}`;
        }
        const counter = document.getElementById('lightbox-counter');
        if (counter) {
            counter.textContent = `${lightboxCurrent + 1} / ${slides.length}`;
        }
    }

    function initLightbox() {
        let overlay = document.getElementById('lightbox-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'lightbox-overlay';
            overlay.className = 'fixed inset-0 z-50 bg-black/90 items-center justify-center p-8';
            overlay.style.display = 'none';
            overlay.innerHTML = `
                <button class="lightbox-close absolute top-6 right-6 text-white text-5xl hover:text-amber z-10" aria-label="Close">&times;</button>
                <button class="lightbox-prev absolute left-6 text-white text-5xl hover:text-amber z-10" aria-label="Previous">❮</button>
                <img id="lightbox-image" class="max-w-[90vw] max-h-[90vh] rounded-xl shadow-2xl object-contain" loading="lazy">
                <button class="lightbox-next absolute right-6 text-white text-5xl hover:text-amber z-10" aria-label="Next">❯</button>
                <div class="absolute bottom-6 left-1/2 -translate-x-1/2 text-white text-sm bg-black/50 px-4 py-2 rounded-full">
                    <span id="lightbox-counter">1 / ${slides.length}</span>
                </div>
            `;
            document.body.appendChild(overlay);

            // Use event delegation for better performance
            overlay.addEventListener('click', function(e) {
                const target = e.target;
                if (target.classList.contains('lightbox-close') || target === overlay) {
                    closeLightbox();
                } else if (target.classList.contains('lightbox-prev')) {
                    e.stopPropagation();
                    navigateLightbox(-1);
                } else if (target.classList.contains('lightbox-next')) {
                    e.stopPropagation();
                    navigateLightbox(1);
                }
            });

            // Keyboard navigation with passive listener
            document.addEventListener('keydown', function(e) {
                if (!lightboxOpen) return;
                if (e.key === 'Escape') {
                    e.preventDefault();
                    closeLightbox();
                } else if (e.key === 'ArrowLeft') {
                    e.preventDefault();
                    navigateLightbox(-1);
                } else if (e.key === 'ArrowRight') {
                    e.preventDefault();
                    navigateLightbox(1);
                }
            });
        }
    }

    // ===== GALLERY GRID =====
    function initGalleryGrid() {
        const galleryGrid = document.getElementById('gallery-grid');
        if (!galleryGrid) return;

        galleryGrid.innerHTML = '';
        galleryGrid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.25rem;
        `;

        const fragment = document.createDocumentFragment();

        slides.forEach((src, index) => {
            const div = document.createElement('div');
            div.className = 'gallery-item';
            div.style.cssText = `
                cursor: pointer;
                overflow: hidden;
                border-radius: 0.5rem;
                transition: transform 0.2s ease;
                position: relative;
                padding-bottom: 75%;
                background: #f0f0f0;
            `;

            const img = document.createElement('img');
            img.loading = 'lazy';
            img.src = src;
            img.className = 'gallery-image';
            img.alt = `Villa photo ${index + 1}`;
            img.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            `;

            div.appendChild(img);

            // Use passive event listeners
            div.addEventListener('mouseenter', function() {
                img.style.transform = 'scale(1.05)';
            }, { passive: true });

            div.addEventListener('mouseleave', function() {
                img.style.transform = 'scale(1)';
            }, { passive: true });

            div.addEventListener('click', function() {
                openLightbox(index);
            });

            fragment.appendChild(div);
        });

        galleryGrid.appendChild(fragment);
    }

    // ===== INITIALIZE EVERYTHING =====
    // Use requestIdleCallback for non-critical initialization
    const init = () => {
        initCarousel();
        initLightbox();
        initGalleryGrid();
        console.log(`Villa gallery initialized with ${slides.length} images`);
    };

    if ('requestIdleCallback' in window) {
        requestIdleCallback(init);
    } else {
        setTimeout(init, 100);
    }
});