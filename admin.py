import urllib.parse

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Filters, MessageHandler
from typing import List
import common
import main
import os

button_list = ['Инструмент', 'Контакты', 'Типовые проекты НТД', 'Кабельная продукция', 'Подключение к дому',
               'Провод СИП', 'Частые Ошибки', 'Коммутационные Аппараты', 'ВЛИ', 'ВЛЗ']  # список кнопок


def admin_start(update: Update, context: CallbackContext) -> None:
    common.read_config_file()

    # Загрузка данных из файла конфигурации
    keyboard = [
        [InlineKeyboardButton("Редактировать код", callback_data='edit_code')]
    ]
    main.user_start(update, context)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Вы вошли как администратор. Выберите действие:', reply_markup=reply_markup)


def edit_code(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    # button_list = ['tool', 'contacts', 'projects', 'cable', 'home_connection',
    #                'sip_cable', 'common_errors', 'switching_devices', 'vli', 'vlz']
    keyboard = [[InlineKeyboardButton(button_name, callback_data=button_name)] for button_name in button_list]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите кнопку для редактирования:", reply_markup=reply_markup)


def edit_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    button_name = query.data
    context.user_data['button_editing'] = button_name
    keyboard = [[InlineKeyboardButton("Загрузить фото", callback_data='upload_photo')],
                [InlineKeyboardButton("Обновить ссылку", callback_data='update_link')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Редактирование кнопки '{button_name}':", reply_markup=reply_markup)


def upload_photo(update: Update, context: CallbackContext) -> None:
    if update.message.photo:
        photo_file = update.message.photo[-1].get_file()
        photo_file.download(custom_path=os.path.join('media', f'{context.user_data["button_editing"]}.jpg'))
        common.config_data[
            f"image_{context.user_data['button_editing']}"] = f'media/{context.user_data["button_editing"]}.jpg'
        save_config_data(common.config_data)
        update.effective_message.reply_text("Фотография успешно загружена!")
        context.bot.send_photo(update.effective_chat.id, photo=photo_file.file_id,
                               caption="Фотография успешно загружена!")
    else:
        update.effective_message.reply_text("Пожалуйста, отправьте фотографию.")


def cancel(update: Update, context: CallbackContext) -> None:
    # query = update.callback_query
    # query.answer()
    if "edit_button_state" in context.user_data:
        del context.user_data["edit_button_state"]
    update.effective_message.reply_text("Редактирование отменено.")


def update_link(update: Update, context: CallbackContext) -> None:
    user = update.callback_query.from_user

    if user.id == int(common.config_data["ADMIN_ID"]):
        text = update.callback_query.message.text
        parsed_text = urllib.parse.urlparse(text)

        if parsed_text.scheme and parsed_text.netloc:
            new_link = text
            common.config_data[f"url_{update.callback_query.message.text}"] = new_link
            save_config_data(common.config_data)
            update.effective_message.reply_text("Ссылка успешно обновлена!")
        else:
            update.effective_message.reply_text("Некорректный формат ссылки.")
    else:
        update.effective_message.reply_text("У вас нет прав для выполнения этой команды.")


def save_config_data(data):
    with open('config.txt', 'w', encoding='utf-8') as f:
        for key, value in data.items():
            f.write(f"{key}: {value}\n")


def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'upload_photo':
        context.user_data['action'] = 'upload_photo'
        update.effective_message.reply_text("Пожалуйста, отправьте фотографию.")
    elif query.data == 'update_photo':
        if 'uploaded_photo' in context.user_data:
            photo_file = context.user_data['uploaded_photo'].get_file()
            photo_file.download(custom_path=os.path.join('media', f'{context.user_data["button_editing"]}.jpg'))
            common.config_data[
                f"image_{context.user_data['button_editing']}"] = f'media/{context.user_data["button_editing"]}.jpg'
            save_config_data(common.config_data)
            update.effective_message.reply_text("Фото успешно обновлено!")
            del context.user_data['uploaded_photo']
        else:
            update.effective_message.reply_text("Сначала загрузите фото.")
    elif query.data in button_list:
        context.user_data['button_editing'] = query.data
        keyboard = [[InlineKeyboardButton("Загрузить фото", callback_data='upload_photo')],
                    [InlineKeyboardButton("Обновить фото", callback_data='update_photo')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Редактирование кнопки '{query.data}':", reply_markup=reply_markup)


def handle_user_reply(update: Update, context: CallbackContext) -> None:
    action = context.user_data.get('action')

    if action == 'upload_photo':
        if update.message.photo:
            photo_file = update.message.photo[-1]
            context.user_data['uploaded_photo'] = photo_file
            update.effective_message.reply_text(
                "Фото успешно загружено! Теперь нажмите 'Обновить фото' для сохранения.")
        else:
            update.message.reply_text("Пожалуйста, отправьте фотографию.")
        del context.user_data['action']


def admin_main() -> None:
    common.read_config_file()
    updater = Updater(common.config_data['token'], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(admin_start))
    dispatcher.add_handler(CommandHandler("edit_code", edit_code))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CommandHandler("admin_start", admin_start))
    # dispatcher.add_handler(CommandHandler("edit_code", edit_code))
    dispatcher.add_handler(MessageHandler(Filters.photo, upload_photo))
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), update_link))
    dispatcher.add_handler(CallbackQueryHandler(callback_handler))
    # dispatcher.add_handler(CommandHandler("callback_handler", callback_handler))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_user_reply))
    # dispatcher.add_handler(MessageHandler(handle_user_reply, handle_user_reply))
    # dispatcher.add_handler(MessageHandler(Filters.photo, process_photo))
    # dispatcher.add_handler(CommandHandler("process_photo", process_photo))
    dispatcher.add_handler(CommandHandler("update_link", update_link))
    dispatcher.add_handler(CommandHandler("save_config_data", save_config_data))
    # dispatcher.add_handler(CallbackQueryHandler(process_photo))  # Move this line above updater.start_polling()
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    admin_main()
