price_text = """
<b>Ура! 🥳 Тепер вам потрібно вказати ціну для вашого замовлення.</b>

<b>🖊 Впишіть, будь ласка, конкретну суму грошей,</b> якщо ви вже визначилися з ціною, наприклад, '1000'.

<b>💰 Але якщо ви ще не визначилися, не переймайтеся!</b>

<b>😊 Ви завжди можете обрати пункт 'Договірна',</b> і тоді ви зможете обговорити ціну пізніше.

"""

description_text = """

<b>Деталі завдання:</b>\n
- Основні завдання та підзавдання 📌
- Вимоги до виконавця 🧑‍💻
- Бажаний термін виконання 📅
- Іншу інформацію, яку вважаєте необхідною 📄\n
Тепер ви можете детально описати всі вимоги, очікування та бажані результати. 🎯
<i>Якщо ви думаєте, що опис не потрібен, і завдання і так зрозуміле, можете залишити це поле пустим. 🤷‍♂️</i> \n
<b>Пам’ятайте:</b> чим більше інформації ви надаєте, тим легше виконавцю буде зрозуміти ваші очікування та правильно виконати завдання! 🌟

"""

adding_materials_text = """

<b>Процес додавання:</b>\n
- Оберіть потрібні файли чи документи 📁
- Завантажте їх на платформу 🔄\n
Додавання правильних та якісних матеріалів допоможе вам і вашій команді ефективно працювати над проектом! 🌟
<i>Будь ласка, дотримуйтеся гідності та коректності при додаванні матеріалів,</i>

"""

deadline_text = """
<b>Введення Дати Дедлайну!</b>
 🌟 Тепер вам потрібно вказати дату дедлайну для виконання завдання!\n
 🚀 Будь ласка, оберіть дату, щоб усі могли ефективно планувати свій час! ⏰

"""

adding_money_text = """
<b>Процес поповнення рахунку:</b>\n
- Введіть потрібну вам суму 📈\n
<i>Будь ласка, будьте уважними під час введення суми та підтвердження операцій,</i>
"""

balance_text = """
<b>Ваш теперішній баланс: {start_data[balance]}</b>

<b>Робота з балансом:</b>\n
- <b>Додати кошти</b>: Оберіть цю опцію, щоб збільшити кількість коштів на вашому рахунку в боті. Вам буде запропоновано можливість ввести потрібну суму самостійно. 📈
- <b>Вивести кошти</b>: Якщо ви хочете зняти частину або всю суму з вашого рахунку, оберіть цю опцію. Після цього дотримуйтеся інструкцій бота для безпечного та швидкого виведення коштів. 📉\n
<i>Будь ласка, будьте обережними під час проведення фінансових операцій та введення даних,</i>
"""

accepting_payment = """
<b>🔵 Підтвердження поповнення</b>\n
<i>Ви обрали суму:</i> <b>{dialog_data[money]}</b> грн\n
🔄 Натисніть на кнопку нижче, щоб підтвердити поповнення рахунку.
"""

redirect_payment_url = """
<b>🔗 Оплата</b>\n
<i>Для здійснення оплати:</i>\n
👉 Натисніть на посилання нижче.
"""

check_password_text = """
<b>🔒 Виведення коштів і доступ до карт</b>\n
<i>Введіть ваш пароль</i> для отримання доступу до банківських карт та можливості виводу коштів.
"""

input_sum_text = """
<b>🔢 Введення суми</b>\n
<b>💱 Ваш баланс: {dialog_data[balance]} грн</b>\n
<i>Будь ласка, введіть суму,</i> яку бажаєте вивести.
"""

choose_card_text = """
<b>🔑 Вибір картки для виведення коштів</b>\n
<i>Будь ласка, оберіть картку</i> для виведення коштів. Якщо ви ще не додавали жодної картки, просимо вас ввести дані картки.
"""

accepting_withdraw_text = """
<b>📋 Інформація про виведення</b>\n
<i>Обрана вами сума:</i> <b>{dialog_data[input_sum]}</b> грн\n
<i>Картка для виведення коштів:</i> <b>{dialog_data[withdrawal_card]}</b>
"""

input_username_text = """
🔹 <b>Введіть своє ім'я користувача</b>🔹\n
Для того, щоб почати роботу з ботом, будь ласка, вкажіть ім'я користувача, яке ви бажаєте використовувати. 
Це ім'я буде використано для ідентифікації ваших дій у боті та забезпечення персоналізованого досвіду.\n
👉 <i>Наприклад</i>: <b>JohnDoe</b>\n
Коли ви введете ім'я користувача, просто надішліть його у цьому чаті.
"""

input_email_text = """
📧 <b>Введіть свій Email</b>\n
Якщо бажаєте отримувати повідомлення на Email або відновити доступ до бота у випадку втрати пароля, будь ласка, вкажіть свою електронну адресу.\n
👉 <i>Наприклад</i>: <b>example@email.com</b>\n
Це необов'язковий крок, але він допоможе підвищити безпеку вашого облікового запису.
"""

input_password_text = """
🔒 <b>Введіть свій пароль</b>\n
Будь ласка, введіть пароль, який ви будете використовувати для входу в бота. Ваш пароль має бути безпечним та унікальним, щоб захистити ваш обліковий запис.\n
👉 <i>Не діліться своїм паролем з іншими особами</i>
"""

input_repeat_text = """
🔑 <b>Повторіть свій пароль</b>\n
Щоб підтвердити, будь ласка, введіть ваш пароль ще раз. Це необхідно для забезпечення того, що пароль було введено без помилок.\n
👉 <i>Переконайтеся, що пароль введено точно так само, як і раніше</i>
"""

auth_text = """
📝 <b>Потрібно зареєструватися в боті для подальшої роботи</b>\n
<b>Перша за все слід додати номер телефону!</b>\n
Щоб продовжити, будь ласка, пройдіть простий процес реєстрації. Реєстрація дозволить вам використовувати всі можливості бота та забезпечить персоналізований досвід.\n
👇 <b>Слідуйте інструкціям нижче, щоб почати:</b>\n
1️⃣ Введіть своє ім'я користувача.
2️⃣ Вкажіть свій Email (опціонально).
3️⃣ Створіть пароль.
4️⃣ Повторіть пароль для підтвердження.
"""

paying_text_accepted = "Замовлення було присвоєне виконавцю!"
