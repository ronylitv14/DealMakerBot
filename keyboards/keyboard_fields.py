from abc import ABCMeta


class KeyboardFields(ABCMeta):
    create_order: str
    my_orders: str
    balance: str
    instruction: str
    executor_profile: str
    client_profile: str
    profile_instruments: str


class ClientKeyboard(KeyboardFields):
    create_order: str = "Cтворити замовлення 📝"
    my_orders: str = "Mої замовлення 📄"
    balance: str = "Баланс 💵"
    instruction: str = 'Інструкція ❗'
    executor_profile: str = "Профіль виконавця 📖"
    client_profile: str = "Профіль замовника 🥳"
    profile_instruments: str = "Налаштування профілю 💂"
    new_deal: str = "Угоди ➕"
    send_number: str = "Відправити номер 😀"
    cancel: str = "Відмінити 🚫"
    # cancel_order: str = "Відмінити замовлення 🚫"


class ExecutorKeyboard(KeyboardFields):
    client_profile: str = "Профіль замовника 🥳"
    my_orders: str = "Mої замовлення 📄"
    profile_instruments: str = "Налаштування профілю 💂"
    balance: str = "Баланс 💵"
    instruction: str = 'Інструкція ❗'
    new_deal: str = "Угоди ➕"
    new_post: str = "Новий пост ✉"
    cancel: str = "Відмінити 🚫"


class ProfileKeyBoard:
    edit_phone: str = "Відредагувати номер телефону ☎"
    edit_password: str = "Відредагувати пароль 🖊"
    edit_name: str = "Відредагувати нік 🧛"
    edit_email: str = "Відредагувати пошту 📪"
    delete_account: str = "Видалити аккаунт ⛔"
    back: str = "Назад 🔙"
