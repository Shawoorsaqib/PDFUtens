/**
 * PDFUtens - About Us Interactive Script
 * Handles scroll entrance animations and animated counters.
 */

document.addEventListener("DOMContentLoaded", () => {
    document.body.classList.add("js-animate");

    // 1. Intersection Observer for Scroll Animations (.fade-up, .fade-in, etc.)
    const animatedElements = document.querySelectorAll(".fade-up, .fade-in, .slide-left, .slide-right");

    const observerOptions = {
        root: null,
        rootMargin: "50px",
        threshold: 0.05
    };

    const animationObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("animated");
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    animatedElements.forEach(el => {
        // If element is already in initial viewport, animate immediately
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight) {
            el.classList.add("animated");
        } else {
            animationObserver.observe(el);
        }
    });

    // 2. Statistics Section Counter Animation
    const statNumbers = document.querySelectorAll(".stat-number[data-target]");
    let countersStarted = false;

    function startCounters() {
        if (countersStarted) return;
        countersStarted = true;

        statNumbers.forEach(counter => {
            const target = parseInt(counter.getAttribute("data-target"), 10) || 0;
            const suffix = counter.getAttribute("data-suffix") || "+";
            const duration = 1600; // ms
            const stepTime = 30; // ms
            const steps = duration / stepTime;
            const increment = target / steps;
            let current = 0;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                counter.textContent = Math.floor(current) + suffix;
            }, stepTime);
        });
    }

    const statsSection = document.querySelector(".stats-section");
    if (statsSection) {
        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    startCounters();
                }
            });
        }, { threshold: 0.3 });

        statsObserver.observe(statsSection);
    }
});
