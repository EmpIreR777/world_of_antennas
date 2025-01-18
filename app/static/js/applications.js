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

// Копирование телефона в буфер обмена
document.addEventListener('DOMContentLoaded', () => {
    const createNotification = (x, y) => {
        const notification = document.createElement('div');
        notification.className = 'copy-notification';
        notification.textContent = 'Номер скопирован';
        
        Object.assign(notification.style, {
            position: 'fixed',
            top: `${y - 70}px`,
            left: `${x}px`,
            transform: 'translate(-50%, -50%) scale(0.9)',
            background: 'linear-gradient(45deg, rgba(255,107,107,0.5), rgba(78,205,196,0.5))',
            color: '#ffffff',
            padding: window.innerWidth <= 768 ? '20px 40px' : '15px 30px',
            fontSize: window.innerWidth <= 768 ? '18px' : '16px',
            borderRadius: '10px',
            zIndex: '9999',
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            opacity: '0'
        });

        document.body.appendChild(notification);
        
        // Анимация появления
        requestAnimationFrame(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translate(-50%, -50%) scale(1)';
        });

        // Удаление уведомления
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translate(-50%, -50%) scale(0.9)';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    };

    const handleCopy = async (e) => {
        e.preventDefault();
        const phone = e.currentTarget.dataset.phone;
        const x = e.type === 'click' ? e.clientX : e.changedTouches[0].clientX;
        const y = e.type === 'click' ? e.clientY : e.changedTouches[0].clientY;

        try {
            await navigator.clipboard.writeText(phone);
            createNotification(x, y);
        } catch (err) {
            console.error('Ошибка копирования:', err);
        }
    };

    document.querySelectorAll('.copy-phone').forEach(element => {
        ['click', 'touchend'].forEach(event => 
            element.addEventListener(event, handleCopy)
        );
    });
});



document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.status-select').forEach(function(select) {
        // Сохраняем начальное значение
        select.setAttribute('data-previous-value', select.value);

        select.addEventListener('change', async function() {
            const applicationId = this.dataset.applicationId;
            const newStatus = this.value;
            const previousValue = this.getAttribute('data-previous-value');

            try {
                const response = await fetch('/api/update-application-status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        application_id: parseInt(applicationId),
                        status: newStatus
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.setAttribute('data-previous-value', newStatus);
                    alert('Статус успешно обновлен');
                } else {
                    this.value = previousValue;
                    alert(data.message || 'Ошибка при обновлении статуса');
                }
            } catch (error) {
                console.error('Ошибка:', error);
                this.value = previousValue;
                alert('Произошла ошибка при обновлении статуса');
            }
        });
    });
});