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

// Функция для отправки нового товара с валидацией
async function submitNewItem(event, workerId) {
    event.preventDefault();

    // Получение значений из полей формы
    const itemNameElement = document.getElementById(`item_name_${workerId}`);
    const quantityElement = document.getElementById(`quantity_${workerId}`);
    const unitTypeElement = document.getElementById(`unit_type_${workerId}`);
    const commentElement = document.getElementById(`comment_${workerId}`);

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
        worker_id: workerId,
        item_name: itemName,
        quantity: quantityNumber,
        unit_type: unitType,
        comment: comment
    };

    try {
        const response = await fetch('/api/create_worker_items', {
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
            throw new Error('Ошибка при добавлении товара');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при добавлении товара');
    }
}

// Функция обновления количества товара
async function updateQuantity(input) {
    const workerId = input.dataset.workerId;
    const itemId = input.dataset.itemId;
    const newQuantity = input.value;

    try {
        const response = await fetch('/api/update_quantity', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                worker_id: workerId,
                item_id: itemId,
                quantity: newQuantity
            })
        });

        if (!response.ok) {
            throw new Error('Ошибка при обновлении количества');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при обновлении количества');
        // Возвращаем предыдущее значение
        input.value = input.defaultValue;
    }
}

// Функция удаления товара
async function deleteItem(workerId, itemId) {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) {
        return;
    }

    try {
        const response = await fetch('/api/delete_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                worker_id: workerId,
                item_id: itemId
            })
        });

        if (response.ok) {
            // Удаляем строку из таблицы
            const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
            if (row) {
                row.remove();
            }
        } else {
            throw new Error('Ошибка при удалении товара');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при удалении товара');
    }
}

// Добавляем обработчики событий при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Можно добавить дополнительную инициализацию при необходимости
});


 /* Функции для увеличения и уменьшения количества */
//  function incrementQuantity(workerId, itemId) {
//     const input = document.getElementById(`quantity_${workerId}_${itemId}`);
//     input.value = parseInt(input.value) + 1;
// }

// function decrementQuantity(workerId, itemId) {
//     const input = document.getElementById(`quantity_${workerId}_${itemId}`);
//     if (parseInt(input.value) > 0) {
//         input.value = parseInt(input.value) - 1;
//     }
// }
