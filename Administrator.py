from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from api.bot_api import start_bot, get_config, terminate
from define import BOT_TOKEN, ADMIN_ID, ADMIN_ID_2


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.id == ADMIN_ID or user.id == ADMIN_ID_2:
        keyboard = [
            ["Запустить", "Завершить плавно", "Завершить"],
            ["Конфиг", "Статистика"],
            ["Депозит", "Плечо", "Количество"],

        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text('Выберите действие:', reply_markup=reply_markup, )


def process_choice(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if text in ["Запустить", "Конфиг", "Статистика"]:
        if text == "Запустить":
            update.message.reply_text(start_bot())
        elif text == 'Конфиг':
            update.message.reply_text(get_config())
        else:
            update.message.reply_text('Операция выполнена')

    elif text in ["Депозит", "Плечо", "Количество"]:
        context.user_data['last_action'] = text
        update.message.reply_text('Введите новое значение:')
    elif text in ["Завершить плавно", "Завершить"]:
        context.user_data['last_action'] = text
        keyboard = [["Да", "Нет"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text('Вы уверены?', reply_markup=reply_markup)


def process_confirmation(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if context.user_data['last_action'] in ["Завершить плавно", "Завершить"]:
        if text == 'Да':
            if context.user_data['last_action'] == 'Завершить':
                update.message.reply_text(terminate())
        else:
            update.message.reply_text('Процедура завершения отменена')
        start(update, context)


def process_input(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    try:
        print(context.user_data['last_action'])
        value = int(text)
        update.message.reply_text('Значение успешно изменено')
        context.user_data['last_action'] = 'None'
        start(update, context)
    except ValueError:
        update.message.reply_text('Введены некорректные данные')
        start(update, context)


def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.regex('^(Да|Нет)$'), process_confirmation))
    dispatcher.add_handler(MessageHandler(
        Filters.regex('^(Запустить|Конфиг|Депозит|Плечо|Количество|Статистика|Завершить плавно|Завершить)$'),
        process_choice))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_input))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()