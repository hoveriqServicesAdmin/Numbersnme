/* ============================================
   NumbersNMe - Common JavaScript
   ============================================ */

// Lazy Load Observer for Elementor backgrounds
const lazyloadRunObserver = () => {
    const lazyloadBackgrounds = document.querySelectorAll(`.e-con.e-parent:not(.e-lazyloaded)`);
    const lazyloadBackgroundObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                let lazyloadBackground = entry.target;
                if (lazyloadBackground) {
                    lazyloadBackground.classList.add('e-lazyloaded');
                }
                lazyloadBackgroundObserver.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: '200px 0px 200px 0px'
    });
    lazyloadBackgrounds.forEach((lazyloadBackground) => {
        lazyloadBackgroundObserver.observe(lazyloadBackground);
    });
};

const events = ['DOMContentLoaded', 'elementor/lazyload/observe'];
events.forEach((event) => {
    document.addEventListener(event, lazyloadRunObserver);
});

// Scroll to Top functionality
document.addEventListener('DOMContentLoaded', function () {
    const scrollTopBtn = document.getElementById('ast-scroll-top');
    if (scrollTopBtn) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 300) {
                scrollTopBtn.style.display = 'block';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });

        scrollTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

// Mobile menu toggle
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function () {
            const expanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !expanded);
            const mobileContent = document.querySelector('.ast-mobile-header-content');
            if (mobileContent) {
                mobileContent.style.display = expanded ? 'none' : 'block';
            }
            document.body.classList.toggle('ast-main-header-nav-open');
        });
    }
});

// Active nav link highlight
document.addEventListener('DOMContentLoaded', function () {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.main-header-menu .menu-link, .ast-mobile-header-content .menu-link');

    navLinks.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href === currentPage) {
            link.closest('.menu-item')?.classList.add('current-menu-item');
        }
    });
});

