// Добавление данных в popup
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


// Добавьте этот код для поля адреса
document.getElementById('address').addEventListener('input', async function(e) {
    const query = e.target.value;
    // Если введено менее 3 символов, не делаем запрос
    if (query.length < 3) return;
    try {
        const response = await fetch(`/suggest-address/?query=${encodeURIComponent(query)}`);
        const suggestions = await response.json();
        // Создаем и показываем выпадающий список с подсказками
        let datalist = document.getElementById('address-suggestions');
        if (!datalist) {
            const newDatalist = document.createElement('datalist');
            newDatalist.id = 'address-suggestions';
            document.body.appendChild(newDatalist);
            datalist = newDatalist;
        }
        // Очищаем старые подсказки
        datalist.innerHTML = '';
        // Добавляем новые подсказки
        suggestions.forEach(suggestion => {const option = document.createElement('option');
            option.value = suggestion.address;
            option.dataset.latitude = suggestion.latitude;
            option.dataset.longitude = suggestion.longitude;
            datalist.appendChild(option);
        });
        // Связываем datalist с input
        e.target.setAttribute('list', 'address-suggestions');
        
    } catch (error) {
        console.error('Error fetching address suggestions:', error);
    }
});


// Добавьте обработчик выбора адреса
document.getElementById('address').addEventListener('change', function(e) {
    const datalist = document.getElementById('address-suggestions');
    const selectedOption = Array.from(datalist.options).find(
        option => option.value === e.target.value
    );
    
    if (selectedOption) {
        document.getElementById('latitude').value = selectedOption.dataset.latitude;
        document.getElementById('longitude').value = selectedOption.dataset.longitude;
    }
});


// Обработчик отправки формы
document.getElementById('closePopup').addEventListener('click', async function () {
    const clientName = document.getElementById('client_name').value.trim();
    const phoneNumber = document.getElementById('phone_number').value.trim();
    const address = document.getElementById('address').value.trim();
    const shop_id = document.getElementById('shop_id').value;
    const service_id = document.getElementById('service_id').value;
    const date = document.getElementById('appointment_date').value;
    const time = document.getElementById('appointment_time').value;
    const comment = document.getElementById('comment').value.trim();
    const userId = document.getElementById('user_id').value;

    // Проверка валидности полей
    if (clientName.length < 2 || clientName.length > 50) {
        alert("Имя должно быть от 2 до 50 символов.");
        return;
    }

    if (phoneNumber && !phoneNumber.match(/^(\+7|8)\d{10}$/)) {
        alert("Введите корректный номер телефона.");
        return;
    }

    if (address.length < 5 || address.length > 100) {
        alert("Адрес должен быть от 5 до 100 символов.");
        return;
    }

    if (!shop_id || !service_id) {
        alert("Выберите магазин и услугу.");
        return;
    }

    // Проверка наличия координат
    const latitude = parseFloat(document.getElementById('latitude').value);
    const longitude = parseFloat(document.getElementById('longitude').value);

    // Проверка широты и долготы
    if (!latitude || !longitude || isNaN(latitude) || isNaN(longitude)) {
        alert("Пожалуйста, выберите адрес из списка подсказок.");
        return;
    }

    // Создаем объект с данными
    const appointmentData = {
        client_name: clientName,
        phone_number: phoneNumber,
        address: address,
        shop_id: shop_id,
        service_id: service_id,
        appointment_date: date,
        appointment_time: time,
        comment: comment,
        user_id: parseInt(userId),
        latitude: latitude,
        longitude: longitude,
    };

    // Преобразуем объект в JSON строку и отправляем POST запрос
    try {
        const response = await fetch('/api/appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(appointmentData)
        });

        if (!response.ok) {
            throw new Error(`Ошибка: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('Response from /api/appointment:', result);

        // Закрываем Telegram WebApp через 100 мс
        setTimeout(() => {
            window.Telegram.WebApp.close();
        }, 100);
    } catch (error) {
        console.error('Error sending POST request:', error);
        alert("Произошла ошибка при отправке заявки. Пожалуйста, попробуйте ещё раз.");
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
    const currentDate = now.toLocaleDateString('en-CA'); // Формат YYYY-MM-DD
    const currentTime = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false }); // Формат HH:MM

    const dateInput = document.getElementById('appointment_date');
    const timeInput = document.getElementById('appointment_time');

    // Установка минимальной даты (сегодня)
    dateInput.min = currentDate;
    dateInput.value = currentDate;

    // Установка максимальной даты (через три месяца)
    const maxDate = new Date(now);
    maxDate.setMonth(maxDate.getMonth() + 3);
    const maxDateISO = maxDate.toLocaleDateString('en-CA'); // Формат YYYY-MM-DD
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

        // Установка текущего времени как значения поля, если оно допустимо
        if (selectedDate === currentDate && currentTime > timeInput.value) {
            timeInput.value = currentTime;
        }
    }

    // Изначально установить минимальное время
    updateMinTime();

    // Установка текущего времени
    timeInput.value = currentTime;

    // Обработчик изменения даты
    dateInput.addEventListener('change', function() {
        if (dateInput.value < currentDate) {
            alert("Выберите дату сегодня или в будущем.");
            dateInput.value = currentDate; // Сбрасываем на минимальную дату
        } else {
            updateMinTime(); // Обновляем минимальное время
        }
    });
});