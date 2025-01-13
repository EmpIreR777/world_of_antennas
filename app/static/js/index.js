// document.addEventListener('DOMContentLoaded', function () {
//     const user = Telegram.WebApp.initDataUnsafe.user;

//     const contactButton = document.getElementById('contact-button');

//     contactButton.addEventListener('click', function () {
//         // Если пользователь существует, добавляем его user_id и first_name в URL, иначе редирект без него
//         if (user && user.id) {
//             window.location.href = `/form?user_id=${user.id}&first_name=${user.first_name}`;
//         } else {
//             window.location.href = `/form`;
//         }
//     });
// });
javascriptdocument.addEventListener('DOMContentLoaded', function () {
    const user = Telegram.WebApp.initDataUnsafe.user;
    const contactButton = document.getElementById('contact-button');

    contactButton.addEventListener('click', function () {
        if (user && user.id) {
            // Запрашиваем контакт пользователя
            Telegram.WebApp.requestContact()
                .then(function(contact) {
                    // После получения контакта перенаправляем на форму с дополнительными данными
                    window.location.href = `/form?user_id=${user.id}&first_name=${user.first_name}&phone=${contact.phone_number}`;
                })
                .catch(function(error) {
                    // Если пользователь отказался предоставить номер или произошла ошибка
                    console.log('Ошибка получения контакта:', error);
                    window.location.href = `/form?user_id=${user.id}&first_name=${user.first_name}`;
                });
        } else {
            window.location.href = '/form';
        }
    });
});
