from os import environ

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from Bin.handlers import *


if 'TELEGRAM_TOKEN' not in environ:
	load_dotenv()
TOKEN = environ.get('TELEGRAM_TOKEN')

updater = Updater(
	TOKEN,
	workers=32,
	request_kwargs={'read_timeout': 60, 'connect_timeout': 60}
)

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('help', help_handler))
dispatcher.add_handler(CommandHandler('cookbook', cookbook_handler))
dispatcher.add_handler(MessageHandler(Filters.reply, reply_handler))
dispatcher.add_handler(MessageHandler(Filters.text, main_handler))

if environ.get('ENVIRONMENT', None) == 'HEROKU':
	print("Starting Webhook")
	updater.start_webhook(
		listen="0.0.0.0",
		port=int(environ.get('PORT')),
		url_path=TOKEN
	)
	updater.bot.setWebhook("https://dankbot-tg.herokuapp.com/" + TOKEN)
	updater.idle()
else:
	print("Starting Polling")
	updater.start_polling()
