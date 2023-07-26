from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import common
import main

button_list = ['tool', 'contacts', 'projects', 'cable', 'home_connection',
               'sip_cable', 'common_errors', 'switching_devices', 'vli', 'vlz']  # список кнопок

button_names = {
    'tool': 'Инструмент',
    'contacts': 'Контакты',
    'projects': 'Типовые проекты НТД',
    'cable': 'Кабельная продукция',
    'home_connection': 'Подключение к дому',
    'sip_cable': 'Провод СИП',
    'common_errors': 'Частые Ошибки',
    'switching_devices': 'Коммутационные Аппараты',
    'vli': 'ВЛИ',
    'vlz': 'ВЛЗ'
}


def admin_start(update: Update, context: CallbackContext) -> None:
    common.read_config_file()

    # Загрузка данных из файла конфигурации
    keyboard = [
        [InlineKeyboardButton("Редактировать код", callback_data='edit_code')]
    ]
    main.user_start(update, context)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text('Вы вошли как администратор. Выберите действие:', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.reply_text('Вы вошли как администратор. Выберите действие:',
                                                 reply_markup=reply_markup)


def edit_code(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = query.from_user

    if user.id == int(common.config_data["ADMIN_ID"]):
        keyboard = [[InlineKeyboardButton(button_names[button_name], callback_data=button_name)] for button_name in
                    button_list]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Выберите кнопку для редактирования:", reply_markup=reply_markup)


def cancel(update: Update, context: CallbackContext) -> None:
    # query = update.callback_query
    # query.answer()
    if "edit_button_state" in context.user_data:
        del context.user_data["edit_button_state"]
    update.effective_message.reply_text("Редактирование отменено.")


def save_config_data(data):
    with open('config.txt', 'w', encoding='utf-8') as f:
        for key, value in data.items():
            f.write(f"{key};{value}\n")


def admin_main() -> None:
    common.read_config_file()
    updater = Updater(common.config_data['token'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(admin_start))
    dispatcher.add_handler(CommandHandler("admin_start", admin_start))
    dispatcher.add_handler(CommandHandler("edit_code", edit_code))
    dispatcher.add_handler(CommandHandler("cancel", cancel))

    dispatcher.add_handler(CommandHandler("save_config_data", save_config_data))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    admin_main()
