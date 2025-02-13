// Функция для переключения отображения формы добавления товара
function toggleAddItemForm(workerId, button) {
    const form = document.getElementById(`add-item-form-${workerId}`);
    
    // Проверяем, отображена ли форма
    if (form.style.display === 'none' || !form.style.display) {
        // Закрываем все открытые формы и показываем соответствующие кнопки
        document.querySelectorAll('.add-item-form').forEach(openForm => {
            openForm.style.display = 'none';
        });
        document.querySelectorAll('.add-item-btn').forEach(btn => {
            btn.style.display = 'inline-block'; // Возвращаем отображение кнопок
        });
        
        // Скрываем текущую кнопку "Добавить товар"
        button.style.display = 'none';
        
        // Показываем форму
        form.style.display = 'block';
    } else {
        // Если форма уже открыта, закрываем её и показываем кнопку
        form.style.display = 'none';
        button.style.display = 'inline-block';
    }
}

// Функция для очистки полей формы и закрытия формы
function clearAddItemForm(workerId) {
    const form = document.getElementById(`add-item-form-${workerId}`);
    if (form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.type === 'number') {
                input.value = input.min || 0; // Устанавливаем минимальное значение или 0
            } else if (input.tagName.toLowerCase() === 'select') {
                input.selectedIndex = 0; // Сбрасываем выбор к первому варианту
            } else {
                input.value = ''; // Сбрасываем текстовые поля и textarea
            }
        });
        // Закрываем форму, скрывая её
        form.style.display = 'none';
        
        // Показываем кнопку "Добавить товар"
        const button = document.querySelector(`button.add-item-btn[onclick*="'${workerId}'"]`);
        if (button) {
            button.style.display = 'inline-block';
        }
    }
}


// Функция для переключения видимости формы добавления товара
function toggleAddItemForm(workerId, button) {
    const form = document.getElementById(`add-item-form-${workerId}`);
    if (form.style.display === 'none') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

// Функция для очистки и скрытия формы добавления товара
function clearAddItemForm(workerId) {
    const form = document.getElementById(`add-item-form-${workerId}`);
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => input.value = '');
    form.style.display = 'none';
}

// Функция для отправки нового товара
async function submitNewItem(event, workerId) {
    event.preventDefault();

    // Получение элементов формы с уникальными ID
    const itemNameElement = document.getElementById(`item_name_${workerId}`);
    const quantityElement = document.getElementById(`quantity_${workerId}`);
    const unitTypeElement = document.getElementById(`unit_type_${workerId}`);
    const commentElement = document.getElementById(`comment_${workerId}`);

    if (!itemNameElement || !quantityElement || !unitTypeElement || !commentElement) {
        console.error('Не удалось найти один из элементов формы.');
        return;
    }

    const itemName = itemNameElement.value.trim();
    const quantity = quantityElement.value.trim();
    const unitType = unitTypeElement.value;
    const comment = commentElement.value.trim();

    // Валидация названия товара (максимум 100 символов)
    if (itemName.length === 0) {
        alert('Название товара не может быть пустым.');
        itemNameElement.focus();
        return;
    }
    if (itemName.length > 100) {
        alert('Название товара не может превышать 100 символов.');
        itemNameElement.focus();
        return;
    }

    // Валидация количества (неотрицательное число)
    const quantityNumber = Number(quantity);
    if (quantity === '' || isNaN(quantityNumber)) {
        alert('Количество должно быть числом.');
        quantityElement.focus();
        return;
    }
    if (quantityNumber < 0) {
        alert('Количество не может быть отрицательным.');
        quantityElement.focus();
        return;
    }

    // Валидация комментария (максимум 200 символов)
    if (comment.length > 200) {
        alert('Комментарий не может превышать 200 символов.');
        commentElement.focus();
        return;
    }

    // Формирование данных для отправки
    const formData = {
        worker_id: Number(workerId),
        item_name: itemName,
        quantity: quantityNumber,
        unit_type: unitType,
        comment: comment
    };

    try {
        const response = await fetch('/worker/create_worker_items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const result = await response.json();
            // Перезагрузка страницы для отображения новых данных
            location.reload();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Ошибка при добавлении товара');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при добавлении товара: ' + error.message);
    }
}


// Функция для обновления количества товара
async function updateQuantity(element) {
    // Получаем workerId и itemId через dataset
    const workerId = element.dataset.workerId;
    const itemId = element.dataset.itemId;
    const newQuantity = element.value;

    // Проверка валидности введенного значения
    if (newQuantity === '' || isNaN(Number(newQuantity)) || Number(newQuantity) < 0) {
        alert('Некорректное количество');
        // Возвращаем предыдущее значение
        element.value = element.defaultValue;
        return;
    }

    const formData = {
        worker_id: Number(workerId),
        item_id: Number(itemId),
        quantity: Number(newQuantity)
    };

    try {
        const response = await fetch('/worker/update_worker_quantity', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            // Можно добавить уведомление об успешном обновлении
            console.log('Количество обновлено успешно');
            // Обновляем defaultValue, чтобы при ошибке возвращалось корректное значение
            element.defaultValue = newQuantity;
        } else {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Ошибка при обновлении количества');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        // Возвращаем предыдущее значение в случае ошибки
        element.value = element.defaultValue;
        alert('Произошла ошибка при обновлении количества: ' + error.message);
    }
}


// Функция для удаления товара
async function deleteItem(workerId, itemId) {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) {
        return;
    }

    try {
        // Формируем URL с GET-параметрами
        const url = `/worker/delete_worker_item?worker_id=${encodeURIComponent(workerId)}&item_id=${encodeURIComponent(itemId)}`;

        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            // Перезагрузка страницы для отображения изменений
            location.reload();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Ошибка при удалении товара');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при удалении товара: ' + error.message);
    }
}
