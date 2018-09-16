from logging import basicConfig, INFO
from random import randint

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

from drake import drake
from fryer import fry_image, fry_gif
from jpeg import jpeg
from vapourize import vapourize
from generator import generate


basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=INFO)

updater = Updater(
	token='622347334:AAHDfULc5msN26uc-i9OZ4t98rtfySEfAgM',
	workers=32,
	request_kwargs={'read_timeout': 25, 'connect_timeout': 25}
)
dispatcher = updater.dispatcher

commands = '''
*Basic Commands*
 1. Hmmmm
 2. Nein
 3. Damnnnn
 4. Allah hu Akbar
 5. Do it
 6. What the
 7. Nigga
 8. F / RIP
 9. E
10. ???
11. Hello there
12. I don't think so
13. Brah wut
14. Miss me with that gay shit / That's gay
15. trollface.jpg

*Advanced Commands*

1. ABC, not XYZ
	Generates a meme using either the Robbie Rotten, Babushka, or Drake template in which ABC is chosen over XYZ.

2. Vapourize:
	Converts text that follows the colon to Vapourwave text and replies to the request.

3. Alexa / Dankbot play Despacito
	Sends a GIF of the Despacito music video along with an audio file of bass boosted Despacito.
	The audio file has a 10% chance of being extremely bass bossted.


Use *>commands* to print all commands and *>cookbook* for frying help.
'''
cookbook = '''
*Deep Fryer*
Fries images, GIFs, or videos.
This includes increasing saturation & contrast, and adding some noise, emojis, lazer eyes, and bulges.
To invoke, reply to a message containing an image, GIF, or video using one of the following commands:

	a) Fry: 1 cycle  of frying.
	b) Nuke: 3 cycles of frying.
	c) Allah hu Akbar: 5 cycles of frying.
	d) Tsar Bomba: 10 cycles of frying.

	Additional commands (Include in the same message):

	a) Deep: High contrast and saturation increase.
	b) Shallow: Low contrast and saturation increase.
	
	c) High-fat: Extra emojis are added.
	d) No-fat: Emojis aren't added.
	
	e) Heavy: Extra bulges are added.
	f) Light: No bulges are added.

Also note that emojis and bulges are disabled by default for GIFs/Videos.
User No-fat/High-fat and Light/Heavy to enable them as needed.


Use *>commands* to print all commands and *>cookbook* for frying help.
'''
keys = ['shallow', 'deep', 'no-fat', 'high-fat', 'light', 'heavy']
cons = 'bcdfghjklmpqrstvwxyz'
nein = [
	'CgADBAADZ6UAAsYeZAetCRQPjvgluwI',
	'CgADBAADeQwAAogaZAeD6-H9IcSaswI'
]


@run_async
def start(bot, update):
	bot.send_message(chat_id=update.message.chat_id, parse_mode='Markdown', text='*This is RipprBot!*\n' + commands)


@run_async
def process(bot, update):
	textn = update.message.text
	text = textn.lower()
	chat_id = update.message.chat_id
	message_id = update.message.message_id

	if update.message.reply_to_message:
		args = {key: 1 if key in text else 0 for key in keys}
		name = update.message.from_user.first_name

		if update.message.reply_to_message.document:
			url = bot.get_file(update.message.reply_to_message.document.file_id).file_path
			fry_gif(
				bot, chat_id, url, name, message_id,
				5 if 'allah hu akbar' in text else 3 if 'nuk' in text else 1 if 'fry' in text else 0,
				args
			)
			return

		elif update.message.reply_to_message.photo:
			url = bot.get_file(update.message.reply_to_message.photo[::-1][0].file_id).file_path
			fry_image(
				bot, chat_id, url, name, message_id,
				5 if 'allah hu akbar' in text else 3 if 'nuk' in text else 1 if 'fry' in text else 0,
				args
			)
			return

	if text == '>commands':
		update.message.reply_text(commands, parse_mode='Markdown')

	elif text == '>cookbook':
		update.message.reply_text(cookbook, parse_mode='Markdown')

	elif 't:' in text and 'b:' in text:
		t = text.find('t:')
		b = text.find('b:')
		if b > t:
			generate(bot, update, textn[t + 2:b], textn[b + 2:])
		else:
			generate(bot, update, textn[t + 2:], textn[b + 2:t])

	elif ', not ' in text:
		drake(bot, update, textn[text.find(', not ') + 6:], textn[:text.find(', not ')])

	elif (update.message.reply_to_message and 'needs' in text and 'jpeg' in text):
		if 'moar' in text:
			jpeg(bot, update, m=2)
		elif 'more' in text:
			jpeg(bot, update, n=3)
		else:
			jpeg(bot, update)

	elif 'vapourize:' in text:
		vapourize(update, textn[text.find('vapourize:') + 10:])

	elif 'alexa play despacito' in text or 'dankbot play despacito' in text:
		bot.send_animation(chat_id, animation='CgADBAADnI4AAmQbZAdH9Tn08dZ_3QI')
		r = randint(0, 9)
		if r:
			bot.send_audio(chat_id, audio='CQADBQADKwADfz25VCqQqUxbbzAhAg')
		else:
			bot.send_audio(chat_id, audio='CQADBQADLAADfz25VH7xA8whBn5dAg')

	elif 'hmmm' in text:
		bot.send_animation(chat_id, animation='CgADBAADCQAD3nJNU7_HSzR8J2dtAg')

	elif 'nein' in text:
		bot.send_animation(chat_id, animation=nein[randint(0, len(nein) - 1)])

	elif 'damnnnn' in text:
		bot.send_animation(chat_id, animation='CgADBAADR4YAApccZAczUrsyn-rCxwI')

	elif 'allah hu akbar' in text:
		bot.send_animation(chat_id, animation='CgADBAADBwMAAsYeZAdmUu3cTHKhGwI')

	elif 'do it' in text:
		print(bot.send_animation(chat_id, animation='CgADBAADgAMAAi4ZZAd8XBGfHNdnhQI'))

	elif 'what the' in text:
		bot.send_photo(chat_id, photo='AgADBQADFagxG64JuVRzEubuAAHg69qMTdUyAAT2Cn1ZV-2hZNOKAwABAg')

	elif 'nigga' in text:
		update.message.reply_text(
			' '.join(
				['🅱️' + x[1:] if x[0].lower() in cons else x for x in textn.split(' ')]
			).replace('g', '🅱️').replace('G', '🅱️')
		)

	elif text == 'f' or text == 'rip':
		update.message.reply_text('F')

	elif text == 'e':
		bot.send_photo(chat_id, photo='AgADBQADSagxG389uVRUovuo9tiKqXcx1TIABKmTrdCdaEhPGJcDAAEC')

	elif text == '???':
		update.message.reply_text('Profit')

	elif 'hello there' in text:
		bot.send_photo(chat_id, photo='AgADBQADFqgxG64JuVTQ1tqZIfI0TDud1jIABGS5QBh2gsTA9BcCAAEC')

	elif 'i don\'t think so' in text or 'i dont think so' in text:
		bot.send_photo(chat_id, photo='AgADBQADF6gxG64JuVRIBsd4VngPrJ811TIABLOsd7lIp3ZiLpcDAAEC')

	elif 'brah wut' in text:
		bot.send_photo(chat_id, photo='AgADBQADRqgxG389uVR8GFE_Qj2BeeVC1jIABJIP9HL4D6o0uI8DAAEC')

	elif 'miss me with that gay shit' in text or 'thats gay' in text or 'that\'s gay' in text:
		bot.send_photo(chat_id, photo='AgADBQADR6gxG389uVT3fIg296WSGNoq1TIABOE4WXAwEZLBxpYDAAEC')

	elif 'trollface.jpg' in text:
		bot.send_photo(chat_id, photo='AgADBQADSKgxG389uVTjpi_5Hditdo5C1jIABHUAAb4etY0ouyWIAwABAg')

	elif 'thought' in text and 'process' in text:
		update.message.reply_text('thoughtprocessors.herokuapp.com')

	elif 'tp' in text:
		update.message.reply_text(
			textn.replace('TP', '✝️🅿️').replace('tp', '✝️🅿️').replace('tP', '✝️🅿️').replace('Tp', '✝️🅿️')
		)

	elif 'jainil' in text:
		update.message.reply_text('ヽ(◉◡◔)ﾉ  i\'M jAiNiL aNd I iS aUtIsTiC. ヽ(◉◡◔)ﾉ')

	else:
		print(update.message.text)


start_handler = CommandHandler('start', start)
message_handler = MessageHandler(Filters.text, process)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(message_handler)

updater.start_polling()
