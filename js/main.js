document.addEventListener('DOMContentLoaded', function () {
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    const savedTheme = localStorage.getItem('python-tutorial-theme');
    if (savedTheme === 'dark') {
        htmlElement.setAttribute('data-theme', 'dark');
    }
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const currentTheme = htmlElement.getAttribute('data-theme');
            if (currentTheme === 'dark') {
                htmlElement.removeAttribute('data-theme');
                localStorage.setItem('python-tutorial-theme', 'light');
            } else {
                htmlElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('python-tutorial-theme', 'dark');
            }
        });
    }
    const burgerMenu = document.getElementById('burgerMenu');
    const mainNav = document.getElementById('mainNav');

    if (burgerMenu && mainNav) {
        burgerMenu.addEventListener('click', function () {
            mainNav.classList.toggle('nav--open');
            const lines = burgerMenu.querySelectorAll('.burger__line');
            if (mainNav.classList.contains('nav--open')) {
                lines[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
                lines[1].style.opacity = '0';
                lines[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
            } else {
                lines[0].style.transform = 'none';
                lines[1].style.opacity = '1';
                lines[2].style.transform = 'none';
            }
        });
        const navLinks = mainNav.querySelectorAll('.nav__link');
        navLinks.forEach(link => {
            link.addEventListener('click', function () {
                mainNav.classList.remove('nav--open');
                const lines = burgerMenu.querySelectorAll('.burger__line');
                lines[0].style.transform = 'none';
                lines[1].style.opacity = '1';
                lines[2].style.transform = 'none';
            });
        });
    }
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    const animateOnScroll = function () {
        const elements = document.querySelectorAll('.feature-card, .step, .audience-card, .why-python__item');

        elements.forEach(el => {
            const rect = el.getBoundingClientRect();
            const windowHeight = window.innerHeight;

            if (rect.top < windowHeight * 0.85) {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }
        });
    };
    const animatedElements = document.querySelectorAll('.feature-card, .step, .audience-card, .why-python__item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    window.addEventListener('load', animateOnScroll);
    window.addEventListener('scroll', animateOnScroll);

    const cardElements = document.querySelectorAll('.lesson-card, .ref-category, .example-card');
    cardElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    });
    const animateCards = function () {
        cardElements.forEach((el, i) => {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight * 0.9) {
                setTimeout(() => {
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                }, i * 60);
            }
        });
    };
    window.addEventListener('load', animateCards);
    window.addEventListener('scroll', animateCards);

    document.querySelectorAll('.code-block__copy').forEach(btn => {
        btn.addEventListener('click', function () {
            const pre = this.closest('.code-block').querySelector('code');
            if (!pre) return;
            navigator.clipboard.writeText(pre.innerText).then(() => {
                const svg = this.querySelector('svg');
                this.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#48BB78" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
                setTimeout(() => {
                    this.innerHTML = svg.outerHTML;
                }, 1500);
            });
        });
    });

    (function () {
        var path = window.location.pathname;
        var isPractice = path.endsWith('practice.html') || path.endsWith('/practice');
        var isAbout = path.endsWith('about.html') || path.endsWith('/about');
        if (!isPractice && !isAbout) {
            var navList = document.querySelector('.nav__list');
            if (navList) {
                navList.insertAdjacentHTML('beforeend',
                    '<li class="nav__item"><a href="/practice.html" class="nav__link">Практика</a></li>' +
                    '<li class="nav__item"><a href="/about.html" class="nav__link">О проекте</a></li>'
                );
            }
        }
    })();

    if (window.location.protocol !== 'file:') {
        const manualAuthPages = ['/register', '/login', '/admin'];
        const currentPath = window.location.pathname;
        const isManual = manualAuthPages.some(p => currentPath === p || currentPath.startsWith(p + '/'));

        if (!isManual) {
            fetch('/api/me')
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    var navList = document.querySelector('.nav__list');
                    if (!navList) return;

                    if (data.logged_in) {
                        if (data.role === 'admin') {
                            navList.insertAdjacentHTML('beforeend',
                                '<li class="nav__item"><a href="/admin" class="nav__link" style="color:var(--color-accent-dark)">&#9733; Панель</a></li>'
                            );
                        }
                        navList.insertAdjacentHTML('beforeend',
                            '<li class="nav__item">' +
                            '<a href="/logout" class="nav__link" style="opacity:.75">' +
                            '<svg style="vertical-align:-2px;margin-right:4px" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>' +
                            data.username +
                            '</a>' +
                            '</li>'
                        );
                    } else {
                        navList.insertAdjacentHTML('beforeend',
                            '<li class="nav__item"><a href="/register" class="nav__link">Регистрация</a></li>' +
                            '<li class="nav__item"><a href="/login" class="nav__link" style="background:rgba(48,105,152,.12);color:var(--color-primary);font-weight:600">Войти</a></li>'
                        );
                    }
                })
                .catch(function () {
                    var navList = document.querySelector('.nav__list');
                    if (navList) {
                        navList.insertAdjacentHTML('beforeend',
                            '<li class="nav__item"><a href="/register" class="nav__link">Регистрация</a></li>' +
                            '<li class="nav__item"><a href="/login" class="nav__link">Войти</a></li>'
                        );
                    }
                });
        }
    }
});