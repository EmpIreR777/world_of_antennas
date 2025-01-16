class AnimationController {
    constructor() {
        this.animatedElements = new Set();
        this.scrollTimeout = null;
        this.observerConfig = {
            threshold: 0.2,
            rootMargin: '50px'
        };
        this.setupIntersectionObserver();
        this.setupEventListeners();
    }

    setupIntersectionObserver() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.animatedElements.has(entry.target)) {
                    this.animateElement(entry.target);
                    this.animatedElements.add(entry.target);
                }
            });
        }, this.observerConfig);
    }

    setupEventListeners() {
        // Обработчик прокрутки
        document.addEventListener('scroll', this.handleScroll.bind(this), {
            passive: true
        });

        // Обработчик изменения размера окна
        window.addEventListener('resize', this.handleResize.bind(this), {
            passive: true
        });

        // Обработчик прокрутки на мобильных устройствах
        const main = document.querySelector('main');
        if (main) {
            main.addEventListener('scroll', this.handleMobileScroll.bind(this), {
                passive: true
            });
        }
    }

    handleScroll() {
        if (this.scrollTimeout) {
            window.cancelAnimationFrame(this.scrollTimeout);
        }

        this.scrollTimeout = window.requestAnimationFrame(() => {
            console.log('Scroll ended');
        });
    }

    handleResize() {
        // Логика для обработки изменения размера окна
        console.log('Window resized');
    }

    handleMobileScroll() {
        if (this.mobileScrollTimeout) {
            clearTimeout(this.mobileScrollTimeout);
        }
        this.mobileScrollTimeout = setTimeout(() => {
            console.log('Mobile scrolling stopped');
        }, 66);
    }

    animateElement(element) {
        const delay = element.dataset.delay || 0;
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, delay);
    }

    observe(elements) {
        elements.forEach(element => {
            // Установка начальных стилей
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            this.observer.observe(element);
        });
    }

    init() {
        const elementsToAnimate = document.querySelectorAll('h1, table');
        
        // Добавление задержек для последовательной анимации
        elementsToAnimate.forEach((el, index) => {
            el.dataset.delay = index * 200;
        });

        // Запуск наблюдения за элементами
        this.observe(elementsToAnimate);
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const animationController = new AnimationController();
    animationController.init();
});

// Запуск начальной анимации при полной загрузке страницы
window.addEventListener('load', () => {
    const elements = document.querySelectorAll('h1, table');
    elements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 200 * index);
    });
});
