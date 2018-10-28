from random import randint

from telegram.ext.dispatcher import run_async

from .drake import drake
from .fryer import fry_image, fry_gif
from .generator import generate
from .jpeg import jpeg
from .vapourize import vapourize

# Misc. Constants
commands = '''
*Basic Commands*
 1. Hmmm
 2. Allah hu Akbar
 3. Do it
 4. Nein
 5. Damnnn
 6. Ironic
 7. F / RIP
 8. ???
 9. Nigga
10. E
11. Hello there
12. I don't think so
13. Wut / Dude what / What even
14. What the
15. Miss me with that gay shit
16. Trollface.jpg

*Advanced Commands*

1. ABC, not XYZ
	Generates a meme using either the Robbie Rotten, Babushka, or Drake template in which ABC is chosen over XYZ.

2. Vapourize:
	Converts text that follows the colon to Vapourwave text and replies to the request.

3. Alexa / Dankbot play Despacito
	Sends a GIF of the Despacito music video along with an audio file of bass boosted Despacito.
	The audio file has a 10% chance of being extremely bass boosted.


Use */help* to print all commands and */cookbook* for frying help.
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

	Additional parameters (Include in the same message):

	a) Deep: High contrast and saturation increase.
	b) Shallow: Low contrast and saturation increase.

	c) High-fat: Emojis are increased.
	d) Low-fat: Emojis are reduced.
	e) No-fat: Emojis aren't added.

	f) Heavy: Extra bulges are added.
	g) Light: No bulges are added.

Also note that emojis and bulges are disabled by default for GIFs/Videos.
Use No-/Low-/High- fat and Light/Heavy to enable them as needed.


Use */help* to print all commands and */cookbook* for frying help.
'''
keys = ['shallow', 'deep', 'no-fat', 'low-fat', 'high-fat', 'light', 'heavy']
cons = 'bcdfghjklmnpqrstvwxyz'
ironic = '''
Did you ever hear the tragedy of Darth Plagueis The Wise?
I thought not. It's not a story the Jedi would tell you.
It's a Sith legend. Darth Plagueis was a Dark Lord of the Sith,
so powerful and so wise he could use the Force to influence the midichlorians to create life…
He had such a knowledge of the dark side that he could even keep the ones he cared about from dying.
The dark side of the Force is a pathway to many abilities some consider to be unnatural. He became so powerful…
The only thing he was afraid of was losing his power, which eventually, of course, he did.
Unfortunately, he taught his apprentice everything he knew, then his apprentice killed him in his sleep.
Ironic. He could save others from death, but not himself.
'''.replace('\n', ' ')
exbuded = ['a', 'an', 'and', 'are', 'if', 'the']

# File IDs - GIFs
hmmm = ['CgADBAADCQAD3nJNU7_HSzR8J2dtAg']
allah_hu_akbar = [
	'CgADBQADMgADUJppVmeCJNTNloNqAg',
	'CgADBAADBwMAAsYeZAdmUu3cTHKhGwI'
]
do_it = ['CgADBAADgAMAAi4ZZAd8XBGfHNdnhQI']
nein = [
	'CgADBAADZ6UAAsYeZAetCRQPjvgluwI',
	'CgADBAADeQwAAogaZAeD6-H9IcSaswI'
]
damnnn = ['CgADBAADR4YAApccZAczUrsyn-rCxwI']

# File IDs - Images
wut = [
	'AgADBQADRqgxG389uVR8GFE_Qj2BeeVC1jIABJIP9HL4D6o0uI8DAAEC',
	'AgADBQADE6gxGyOkIFbed8kggNlVrg9m2zIABHSNs_wtRkJAA2UAAgI',
	'AgADBQADFKgxGyOkIFYEvB40ArE8y0Ji2zIABLXKY5s3F2UkFWQAAgI',
	'AgADBQADZ6gxG0uLKVYZ-d7qyUcW-26j1jIABJRPBU5rooV21gwDAAEC'
]
what_the = ['AgADBQADFagxG64JuVRzEubuAAHg69qMTdUyAAT2Cn1ZV-2hZNOKAwABAg']
miss_me = ['AgADBQADR6gxG389uVT3fIg296WSGNoq1TIABOE4WXAwEZLBxpYDAAEC']


@run_async
def start_handler(bot, update):
	update.message.reply_markdown(text='*This is RipprBot!*\n' + commands)


@run_async
def help_handler(bot, update):
	update.message.reply_markdown(text=commands)


@run_async
def cookbook_handler(bot, update):
	update.message.reply_markdown(text=cookbook)


@run_async
def reply_handler(bot, update):
	textn = update.message.text
	text = textn.lower()
	name = update.message.from_user.first_name
	chat_id = update.message.chat_id
	message_id = update.message.message_id

	n = (10 if 'tsar bomba' in text else
	     5 if 'allah hu akbar' in text else
	     3 if 'nuk' in text else
	     1 if 'fry' in text else 0)

	if n:
		args = {key: 1 if key in text else 0 for key in keys}
		if update.message.reply_to_message.document:
			url = bot.get_file(update.message.reply_to_message.document.file_id).file_path
			fry_gif(update, url, n, args)
			return

		elif update.message.reply_to_message.video:
			url = bot.get_file(update.message.reply_to_message.video.file_id).file_path
			fry_gif(update, url, n, args)
			return

		elif update.message.reply_to_message.photo:
			url = bot.get_file(update.message.reply_to_message.photo[::-1][0].file_id).file_path
			fry_image(update, url, n, args)
			return

	elif ('t:' in text or 'ts:' in text) and ('b:' in text or 'bs:' in text):
		t, tc = (text.find('t:'), 1) if 't:' in text else (text.find('ts:'), 0)
		b, bc = (text.find('b:'), 1) if 'b:' in text else (text.find('bs:'), 0)
		url = bot.get_file(update.message.reply_to_message.photo[::-1][0].file_id).file_path

		if b > t:
			generate(
				update, url,
				textn[t + 2:b].upper() if tc else textn[t + 3:b],
				textn[b + 2:].upper() if bc else textn[b + 3:]
			)
		else:
			generate(
				update, url,
				textn[t + 2:].upper() if tc else textn[t + 3:],
				textn[b + 2:t].upper() if bc else textn[b + 3:t]
			)
		return
	main_handler(bot, update)


@run_async
def main_handler(bot, update):
	textn = update.message.text
	text = textn.lower()

	if ', not ' in text:
		drake(update, textn[text.find(', not ') + 6:], textn[:text.find(', not ')])

	elif (update.message.reply_to_message and 'needs' in text and 'jpeg' in text):
		url = bot.get_file(update.message.reply_to_message.photo[::-1][0].file_id).file_path
		if 'much' in text:
			jpeg(update, url, m=3)
		elif 'moar' in text:
			jpeg(update, url, m=2)
		elif 'more' in text:
			jpeg(update, url, n=3)
		else:
			jpeg(update, url)

	elif 'vapourize:' in text:
		vapourize(update, textn[text.find('vapourize:') + 10:])

	elif 'alexa play despacito' in text or 'dankbot play despacito' in text:
		update.message.reply_animation(animation='CgADBAADnI4AAmQbZAdH9Tn08dZ_3QI')
		r = randint(0, 9)
		if r:
			update.message.reply_audio(audio='CQADBQADKwADfz25VCqQqUxbbzAhAg')
		else:
			update.message.reply_audio(audio='CQADBQADLAADfz25VH7xA8whBn5dAg')

	elif 'hmmm' in text:
		update.message.reply_animation(animation=hmmm[randint(0, len(hmmm) - 1)])

	elif 'allah hu akbar' in text:
		update.message.reply_animation(animation=allah_hu_akbar[randint(0, len(allah_hu_akbar) - 1)])

	elif 'do it' in text:
		update.message.reply_animation(animation=do_it[randint(0, len(do_it) - 1)])

	elif 'nein' in text:
		update.message.reply_animation(animation=nein[randint(0, len(nein) - 1)])

	elif 'damnnn' in text:
		update.message.reply_animation(animation=damnnn[randint(0, len(damnnn) - 1)])

	elif 'ironic' in text or 'darth plagueis' in text:
		update.message.reply_text(ironic)

	elif text == 'f' or text == 'rip':
		update.message.reply_text('F')

	elif text == '???':
		update.message.reply_text('Profit')

	elif 'nigga' in text or '🅱️' in text:
		a = []
		for x in text.split(' '):
			if x == 'nigga':
				a.append('ni🅱️🅱️a')
				continue
			if x in exbuded:
				a.append(x)
				continue
			i = 0
			try:
				while x[i] not in cons:
					i += 1
				s, i = i, i + 1
				while x[i] in cons:
					i += 1
				e = i
				a.append(x[:s] + '🅱️' + x[e:])
			except IndexError:
				a.append(x)
		update.message.reply_text(' '.join(a))

	elif text == 'e':
		update.message.reply_photo(photo='AgADBQADSagxG389uVRUovuo9tiKqXcx1TIABKmTrdCdaEhPGJcDAAEC')

	elif 'hello there' in text:
		update.message.reply_photo(photo='AgADBQADFqgxG64JuVTQ1tqZIfI0TDud1jIABGS5QBh2gsTA9BcCAAEC')

	elif 'i don\'t think so' in text or 'i dont think so' in text:
		update.message.reply_photo(photo='AgADBQADF6gxG64JuVRIBsd4VngPrJ811TIABLOsd7lIp3ZiLpcDAAEC')

	elif 'wut' in text or 'dude what' in text or 'what even' in text:
		update.message.reply_photo(photo=wut[randint(0, len(wut) - 1)])

	elif 'what the' in text:
		update.message.reply_photo(photo=what_the[randint(0, len(what_the) - 1)])

	elif 'miss me with that gay shit' in text or 'thats gay' in text or 'that\'s gay' in text:
		update.message.reply_photo(photo=miss_me[randint(0, len(miss_me) - 1)])

	elif 'trollface.jpg' in text:
		update.message.reply_photo(photo='AgADBQADSKgxG389uVTjpi_5Hditdo5C1jIABHUAAb4etY0ouyWIAwABAg')

	elif 'thought' in text and 'process' in text:
		update.message.reply_text('thoughtprocessors.herokuapp.com')

	elif 'tp' in text:
		update.message.reply_text(
			textn.replace('TP', '✝️🅿️').replace('tp', '✝️🅿️').replace('tP', '✝️🅿️').replace('Tp', '✝️🅿️')
		)

	elif 'jainil' in text:
		update.message.reply_text('ヽ(◉◡◔)ﾉ  i\'M jAiNiL aNd I iS aUtIsTiC. ヽ(◉◡◔)ﾉ')

	else:
		print(
			'(%s) %s: %s' % (update.message.chat.title, update.message.from_user.first_name, textn)
			if update.message.chat.type == 'group' else
			'%s: %s' % (update.message.from_user.first_name, textn)
		)
