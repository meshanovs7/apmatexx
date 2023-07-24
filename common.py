from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

import main
import admin

config_data = {}


def read_config_file():
    global config_data
    with open("config.txt", "r+", encoding='utf-8') as file:
        rawfile = file.readlines()
        for line in rawfile:
            file_data = line.strip().split(';')
            if file_data:
                var_name = file_data[0]
                var_value = file_data[1]
                config_data[var_name] = var_value
                print(config_data['token'])


def admin_check(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.id == int(config_data.get("ADMIN_ID", 0)):
        admin.admin_start(update, context)  # Предполагается, что в administrator.py есть функция start()
    else:
        main.user_start(update, context)
        # Обычное поведение для не-админов

# def common_start(update: Update, context: CallbackContext) -> None:
#     read_config_file()  # Загрузка данных из файла конфигурации
#     admin_check(update, context)
# keyboard = [
#     [InlineKeyboardButton("Инструмент", callback_data='tool')],
#     [InlineKeyboardButton("Контакты", callback_data='contacts')],
#     [InlineKeyboardButton("Типовые проекты НТД", callback_data='projects')],
#     [InlineKeyboardButton("Кабельная продукция", callback_data='cable')],
#     [InlineKeyboardButton("Воздушные линии", callback_data='airlines')]
# ]
# reply_markup = InlineKeyboardMarkup(keyboard)
# update.effective_message.reply_text('Выберите действие:',
#                                     reply_markup=reply_markup)


# def common_button(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     query.answer()
#     # Логика для обычного пользователя
#     if query.data in ['tool', 'contacts', 'projects', 'cable', 'home_connection', 'sip_cable', 'common_errors',
#                       'switching_devices', 'vli', 'vlz']:
#         photo_path = config_data[f"image_{query.data}"]
#         link = config_data[f"url_{query.data}"]
#         description = f'Описание {query.data}. [Подробнее]({link})'
#         keyboard = [[InlineKeyboardButton("Назад", callback_data='back')]
#
#                     ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         try:
#             with open(photo_path, 'rb+') as photo_file:
#                 context.bot.send_photo(chat_id=query.message.chat_id, photo=photo_file, caption=description,
#                                        reply_markup=reply_markup)
#         except Exception as e:
#             query.edit_message_text(f"Произошла ошибка при открытии файла: {e}")
#     elif query.data == 'airlines':
#         # Логика для кнопки 'airlines'
#         keyboard = [
#             [InlineKeyboardButton("Подключение к дому", callback_data='home_connection')],
#             [InlineKeyboardButton("Провод СИП", callback_data='sip_cable')],
#             [InlineKeyboardButton("Частые Ошибки", callback_data='common_errors')],
#             [InlineKeyboardButton("Коммутационные Аппараты", callback_data='switching_devices')],
#             [InlineKeyboardButton("Арматура для Магистрали", callback_data='armature')],
#             [InlineKeyboardButton("Назад", callback_data='back')]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         query.edit_message_text(text="Меню \"воздушные линии.Выберите интересующую вас категорию из меню ниже:",
#                                 reply_markup=reply_markup)
#     elif query.data == 'back_1':
#         # Логика для кнопки 'back'
#         query.edit_message_text(text="Меню \"воздушные линии.Выберите интересующую вас категорию из меню ниже:")
#     elif query.data == 'back':
#         # Логика для кнопки 'back'
#         common_start(update, context)
#
#     elif query.data == 'armature':
#         # Логика для кнопки 'Арматура для Магистрали'
#         keyboard = [
#             [InlineKeyboardButton("ВЛИ", callback_data='vli')],
#             [InlineKeyboardButton("ВЛЗ", callback_data='vlz')],
#             [InlineKeyboardButton("Назад", callback_data='back')]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         query.edit_message_text(text="Выберите интересующую вас категорию из меню ниже:", reply_markup=reply_markup)
#     elif query.data == 'vli' or query.data == 'vlz':
#         # Логика для кнопок 'ВЛИ' и 'ВЛЗ'
#         # Добавьте здесь вашу логику для кнопок 'ВЛИ' и 'ВЛЗ'
#         pass
#     elif query.data == 'airlines_category':
#         # Логика для категории воздушных линий
#         # Добавьте здесь вашу логику для категории воздушных линий
#         pass


# def start_bot(dispatcher) -> None:
#     read_config_file()
#     updater = Updater(config_data['token'], use_context=True)
#     dispatcher = updater.dispatcher
#     # dispatcher.add_handler(CommandHandler("common_start", common_start))
# dispatcher.add_handler(CommandHandler("admin_check", admin_check))
# dispatcher.add_handler(CallbackQueryHandler(common_button))
# dispatcher.add_handler(MessageHandler(
#     Filters.regex(
#         '^(update_photo|update_link|save_config_data|tool|contacts|projects|cable|airlines)$'),
#     common_button))
# updater.start_polling()
# updater.idle()
