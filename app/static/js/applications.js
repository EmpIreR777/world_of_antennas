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

        // Установка позиции через inline-стили
        Object.assign(notification.style, {
            top: `${y - 70}px`,
            left: `${x}px`,
            position: 'fixed',
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
        // Определение координат клика или касания
        let x, y;
        if (e.type === 'click') {
            x = e.clientX;
            y = e.clientY;
        } else if (e.type === 'touchend' && e.changedTouches.length > 0) {
            x = e.changedTouches[0].clientX;
            y = e.changedTouches[0].clientY;
        } else {
            // Если координаты определить невозможно, установить центр окна
            x = window.innerWidth / 2;
            y = window.innerHeight / 2;
        }

        try {
            await navigator.clipboard.writeText(phone);
            createNotification(x, y);
        } catch (err) {
            console.error('Ошибка копирования:', err);
            // Альтернативное уведомление при ошибке копирования
            alert('Не удалось скопировать номер.');
        }
    };

    document.querySelectorAll('.copy-phone').forEach(element => {
        ['click', 'touchend'].forEach(event => 
            element.addEventListener(event, handleCopy)
        );
    });
});


// Обновление статуса заявки
document.addEventListener('DOMContentLoaded', () => {
    const masterId = document.getElementById('worker_id').getAttribute('value');

    if (!masterId) {
        console.error('Не удалось получить master_id текущего пользователя.');
        return;
    }

    const statusSelects = document.querySelectorAll('.status-select');

    statusSelects.forEach(select => {
        select.addEventListener('change', async (event) => {
            const newStatus = event.target.value;
            const row = event.target.closest('tr');
            const applicationId = row.getAttribute('data-application-id');

            const payload = {
                application_id: parseInt(applicationId),
                status: newStatus,
                master_id: parseInt(masterId)
            };

            console.log("Отправляемый JSON:", JSON.stringify(payload));

            try {
                const response = await fetch('/update-application-status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.success) {
                        alert('Статус обновлен успешно.');
                    } else {
                        alert('Ошибка при обновлении статуса: ' + result.message);
                        // Опционально: восстановить предыдущее значение
                    }
                } else {
                    const errorText = await response.text();
                    alert('Ошибка сервера: ' + errorText);
                }
            } catch (error) {
                console.error('Ошибка при отправке запроса:', error);
                alert('Произошла ошибка при отправке запроса.');
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('appointments-table');
    const headers = table.querySelectorAll('th[data-sort]');
    const tbody = table.querySelector('tbody');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const sortBy = header.getAttribute('data-sort');
            const isAscending = header.classList.toggle('asc');
            sortTable(sortBy, isAscending);
        });
    });

    function sortTable(sortBy, isAscending) {
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            const aValue = a.querySelector(`td[data-${sortBy}]`).getAttribute(`data-${sortBy}`);
            const bValue = b.querySelector(`td[data-${sortBy}]`).getAttribute(`data-${sortBy}`);

            if (aValue < bValue) return isAscending ? -1 : 1;
            if (aValue > bValue) return isAscending ? 1 : -1;
            return 0;
        });

        // Очистите таблицу и добавьте отсортированные строки
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }
});