import os
import urllib.parse
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import admin
import common


def start(update: Update, context: CallbackContext) -> None:
    common.admin_check(update, context)


def user_start(update: Update, context: CallbackContext) -> None:
    common.read_config_file()

    keyboard = [
        [InlineKeyboardButton("Инструмент", callback_data='tool')],
        [InlineKeyboardButton("Контакты", callback_data='contacts')],
        [InlineKeyboardButton("Типовые проекты НТД", callback_data='projects')],
        [InlineKeyboardButton("Кабельная продукция", callback_data='cable')],
        [InlineKeyboardButton("Воздушные линии", callback_data='airlines')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text('Добро пожаловать! Выберите интересующую вас категорию:',
                                        reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    button_data = query.data
    buttons = ['tool', 'contacts', 'projects', 'cable', 'home_connection', 'sip_cable', 'common_errors',
               'switching_devices', 'vli', 'vlz']

    if button_data in buttons:
        photo_path = common.config_data[f"image_{button_data}"]
        link = common.config_data[f"url_{button_data}"]
        description = f'Описание {button_data}. [Подробнее]({link})'
        keyboard = [[InlineKeyboardButton("На главную", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open(photo_path, 'rb+') as photo_file:
                context.bot.send_photo(chat_id=query.message.chat_id, photo=photo_file, caption=description,
                                       reply_markup=reply_markup)
        except Exception as e:
            keyboard = [[InlineKeyboardButton("Назад", callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(f"Произошла ошибка при открытии файла: {e}", reply_markup=reply_markup)

    elif query.data == 'airlines':
        airlines_category(update, context)
    elif query.data == 'back':
        common.admin_check(update, context)
    elif query.data == 'back_2':
        airlines_category(update, context)
    elif query.data == 'armature':
        armature_menu(update, context)
    elif query.data == 'edit_code':
        admin.edit_code(update, context)
    elif query.data == 'update_link':
        update_link(update, context)
    elif query.data == 'save_config_data':
        admin.save_config_data(update)
    elif query.data == 'cancel':
        admin.cancel(update, context)
    elif query.data == 'update_link':
        update_link(update, context)
    if query.data == 'upload_photo':
        context.user_data['action'] = 'upload_photo'
        update.effective_message.reply_text("Пожалуйста, отправьте изображение.")
    elif query.data == 'update_photo':
        if 'uploaded_photo' in context.user_data:
            photo_file = context.user_data['uploaded_photo'].get_file()
            photo_file.download(custom_path=os.path.join('media', f'{context.user_data["button_editing"]}.jpg'))
            common.config_data[
                f"image_{context.user_data['button_editing']}"] = f'media/{context.user_data["button_editing"]}.jpg'
            admin.save_config_data(common.config_data)
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
            update.effective_message.reply_text("Фото успешно обновлено!", reply_markup=reply_markup)
            del context.user_data['uploaded_photo']
        else:
            update.effective_message.reply_text("Сначала загрузите фото.")
    elif query.data in admin.button_list:
        user = query.from_user
        if user.id == int(common.config_data["ADMIN_ID"]):
            context.user_data['button_editing'] = query.data
            keyboard = [[InlineKeyboardButton("Загрузить фото", callback_data='upload_photo')],
                        [InlineKeyboardButton("Обновить ссылку", callback_data='update_link')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=f"Редактирование кнопки '{query.data}';", reply_markup=reply_markup)


def handle_user_reply(update: Update, context: CallbackContext) -> None:
    action = context.user_data.get('action')

    if action == 'upload_photo':
        if update.message.photo:
            photo_file = update.message.photo[-1]
            context.user_data['uploaded_photo'] = photo_file
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Обновить фото", callback_data='update_photo')]])
            update.effective_message.reply_text(
                "Фото успешно загружено! Теперь нажмите 'Обновить фото' для сохранения.", reply_markup=reply_markup)
        else:
            update.message.reply_text("Пожалуйста, отправьте фотографию.")
        del context.user_data['action']

    elif action == 'update_link':
        if update.message.text:
            text = update.effective_message.text.strip()
            parsed_text = urllib.parse.urlparse(text)
            if parsed_text.scheme and parsed_text.netloc:
                new_link = text
                button_text = context.user_data['button_editing']
                common.config_data[f"url_{button_text}"] = new_link
                admin.save_config_data(common.config_data)
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='back')]])
                update.effective_message.reply_text("Ссылка успешно обновлена!", reply_markup=reply_markup)
            else:
                update.effective_message.reply_text("Некорректный формат ссылки.")
        else:
            update.message.reply_text("Отправьте корректную ссылку.")
        context.user_data.pop('action', None)  # Безопасное удаление ключа 'action'


def update_link(update: Update, context: CallbackContext) -> None:
    user = update.callback_query.from_user
    if user.id == int(common.config_data["ADMIN_ID"]):
        if update.effective_message:
            update.effective_message.reply_text("Отправьте ссылку для обновления:")
            context.user_data['action'] = 'update_link'  # Сохраняем действие в user_data
        else:
            update.effective_message.reply_text("Сообщение отсутствует.")
    else:
        update.effective_message.reply_text("У вас нет прав для выполнения этой команды.")


def airlines_category(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Подключение к дому", callback_data='home_connection')],
        [InlineKeyboardButton("Провод СИП", callback_data='sip_cable')],
        [InlineKeyboardButton("Частые Ошибки", callback_data='common_errors')],
        [InlineKeyboardButton("Коммутационные Аппараты", callback_data='switching_devices')],
        [InlineKeyboardButton("Арматура для Магистрали", callback_data='armature')],
        [InlineKeyboardButton("На главную", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Меню воздушные линии. Выберите интересующую вас категорию из меню ниже:",
                            reply_markup=reply_markup)


def armature_menu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("ВЛИ", callback_data='vli')],
        [InlineKeyboardButton("ВЛЗ", callback_data='vlz')],
        [InlineKeyboardButton("Назад в Воздушные линии", callback_data='back_2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите интересующую вас категорию из меню ниже:", reply_markup=reply_markup)


def main() -> None:
    common.read_config_file()
    updater = Updater(common.config_data['token'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CallbackQueryHandler(start))
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(airlines_category))
    dispatcher.add_handler(CallbackQueryHandler(armature_menu))
    dispatcher.add_handler(CommandHandler("user_start", user_start))
    dispatcher.add_handler(CommandHandler("button", button))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))
    dispatcher.add_handler(CallbackQueryHandler(update_link, pattern='^update_link$'))
    dispatcher.add_handler(CommandHandler("update_link", update_link))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
