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
                if len(file_data) < 2:
                    print(f"В строке '{line}' не хватает данных")
                    continue
                var_name = file_data[0]
                var_value = file_data[1]
                config_data[var_name] = var_value


def admin_check(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if user.id == int(config_data.get("ADMIN_ID", 0)):
        admin.admin_start(update, context)
    else:
        main.user_start(update, context)

