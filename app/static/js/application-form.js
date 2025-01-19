document.getElementById('applicationForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('client_name').value;
    const serviceSelect = document.getElementById('service_id');
    const serviceName = serviceSelect.options[serviceSelect.selectedIndex].text;
    const date = document.getElementById('appointment_date').value;
    const time = document.getElementById('appointment_time').value;

    const fullMessage = `${name}, ваша заявка на <strong>${serviceName.toLowerCase()}</strong> оформлена ${date} в ${time}.\n Ожидайте звонка для уточнения деталей заявки`;
    document.getElementById('popupMessage').style.whiteSpace = 'pre-line';
    document.getElementById('popupMessage').innerHTML = fullMessage;
    document.getElementById('popup').style.display = 'flex';
});

document.getElementById('closePopup').addEventListener('click', async function () {
    const clientName = document.getElementById('client_name').value.trim();
    const phoneNumber = document.getElementById('phone_number').value.trim();
    const address = document.getElementById('address').value.trim();
    const shop = document.getElementById('shop_id').value;
    const service = document.getElementById('service_id').value;
    const date = document.getElementById('appointment_date').value;
    const time = document.getElementById('appointment_time').value;
    const comment = document.getElementById('comment').value.trim();
    const userId = document.getElementById('user_id').value;

    // Проверка валидности полей
    if (clientName.length < 2 || clientName.length > 50) {
        alert("Имя должно быть от 2 до 50 символов.");
        return;
    }

    if (phoneNumber && !phoneNumber.match(/^[0-9+]{10,15}$/)) {
        alert("Введите корректный номер телефона.");
        return;
    }

    if (address.length < 5 || address.length > 100) {
        alert("Адрес должен быть от 5 до 100 символов.");
        return;
    }

    if (!shop || !service) {
        alert("Выберите магазин и услугу.");
        return;
    }

    // Создаем объект с данными
    const appointmentData = {
        client_name: clientName,
        phone_number: phoneNumber,
        address: address,
        shop: shop,
        service: service,
        appointment_date: date,
        appointment_time: time,
        comment: comment,
        user_id: parseInt(userId)
    };

    // Преобразуем объект в JSON строку
    const jsonData = JSON.stringify(appointmentData);

    // Отправляем POST запрос
    try {
        const response = await fetch('/api/appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: jsonData
        });
        const result = await response.json();
        console.log('Response from /form:', result);

        // Закрываем Telegram WebApp через 100 мс
        setTimeout(() => {
            window.Telegram.WebApp.close();
        }, 100);
    } catch (error) {
        console.error('Error sending POST request:', error);
    }
});


// Анимация и остальной код остается без изменений
function animateElements() {
    const elements = document.querySelectorAll('h1, .form-group, .btn');
    elements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

// Стили для анимации
var styleSheet = document.styleSheets[0];
styleSheet.insertRule(`
    h1, .form-group, .btn {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.5s ease, transform 0.5s ease;
    }
`, styleSheet.cssRules.length);

styleSheet.insertRule(`
    body {
        opacity: 0;
        transition: opacity 0.5s ease;
    }
`, styleSheet.cssRules.length);

// Плавное появление страницы при загрузке
window.addEventListener('load', function () {
    document.body.style.opacity = '1';
    animateElements();
});
styleSheet.insertRule(`
    body {
        opacity: 0;
        transition: opacity 0.5s ease;
`, styleSheet.cssRules.length);

// Добавляем текущую дату и время в поле даты
document.addEventListener('DOMContentLoaded', function() {
    const now = new Date();
    const currentDate = now.toISOString().split('T')[0];
    const currentTime = now.toTimeString().slice(0,5);
    
    const dateInput = document.getElementById('appointment_date');
    const timeInput = document.getElementById('appointment_time');

    // Установка минимальной даты (сегодня)
    dateInput.min = currentDate;
    dateInput.value = currentDate;

    // Установка максимальной даты (через три месяца)
    const maxDate = new Date(now);
    maxDate.setMonth(maxDate.getMonth() + 3);
    // Обработка случая, когда текущая дата — 31-е, а целевой месяц меньше
    const maxDateISO = maxDate.toISOString().split('T')[0];
    dateInput.max = maxDateISO;

    // Функция для обновления минимального времени
    function updateMinTime() {
        const selectedDate = dateInput.value;
        if (selectedDate === currentDate) {
            // Если выбрана сегодняшняя дата, установить минимальное время как текущее
            timeInput.min = currentTime;
        } else {
            // Иначе установить минимальное время на начало дня
            timeInput.min = '00:00';
        }

        // Опционально: установить текущее время как значение по умолчанию, если оно допустимо
        // Проверяем, чтобы текущее время не позже максимального
        if (selectedDate === currentDate && currentTime > timeInput.value) {
            timeInput.value = currentTime;
        }
    }

    // Изначально установить минимальное время
    updateMinTime();

    // Обновлять минимальное время при изменении даты
    dateInput.addEventListener('change', updateMinTime);
});