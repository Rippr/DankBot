from io import BytesIO
from os import remove
from os.path import abspath, split as path_split
from random import shuffle
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

from PIL import Image
from cv2 import CAP_PROP_FPS, COLOR_BGR2RGB, COLOR_RGB2BGR, \
	VideoWriter, VideoWriter_fourcc, cvtColor
from imutils.video import FileVideoStream
from numpy import array
from time import sleep

from bin.fryer import __colorize, __fry, __get_caption, __increase_contrast, \
	__posterize, __sharpen, __upload_to_imgur

bin_path = path_split(abspath(__file__))[0]


def fry_gif(update, url, number_of_cycles, args):
	number_of_emojis = 1.5 if args['high-fat'] else 1 if args['low-fat'] else 0
	bulge_probability = 0.3 if args['heavy'] else 0.15 if args['light'] else 0
	magnitude = 4 if args['deep'] else 1 if args['shallow'] else 2

	name = update.message.from_user.first_name
	filename = '%s_%s_%s' % (
		update.message.chat_id,
		name,
		update.message.message_id
	)
	filepath = f'{bin_path}/temp/{filename}'
	caption = __get_caption(name, number_of_cycles, args)
	output = f'{bin_path}/temp/out_{filename}.mp4'

	gif_bio = BytesIO()
	gif_bio.name = f'{filename}.gif'
	fs = [__posterize, __sharpen, __increase_contrast, __colorize]
	shuffle(fs)

	if not __download_gif(url, filepath):
		return

	fvs = FileVideoStream(f'{filepath}.mp4').start()
	frame = fvs.read()
	height, width, _ = frame.shape

	try:
		fps = fvs.get(CAP_PROP_FPS)
	except:
		fps = 30
	out = VideoWriter(
		output, VideoWriter_fourcc(*'mp4v'), fps, (width, height)
	)
	out.write(fry_frame(
		frame, number_of_cycles, fs, number_of_emojis,
		bulge_probability, magnitude, args
	))

	while fvs.more() or fvs.more():
		try:
			temp = fry_frame(
				fvs.read(), number_of_cycles, fs, number_of_emojis,
				bulge_probability, magnitude, args
			)
		except Exception:
			break
		out.write(temp)

	fvs.stop()
	fvs.stream.release()
	out.release()
	update.message.reply_animation(
		open(output, 'rb'),
		caption=caption,
		quote=True
	)
	try:
		__upload_to_imgur(output, caption)
	except (Exception, BaseException) as e:
		print(e)
	remove(f'{filepath}.mp4')


def fry_frame(
		frame, number_of_cycles, fs, number_of_emojis,
		bulge_probability, magnitude, args
):
	img = Image.fromarray(cvtColor(frame, COLOR_BGR2RGB))
	img = __fry(
		img, number_of_cycles, number_of_emojis,
		bulge_probability, args['chilli'], args['vitamin-b']
	)

	for _ in range(number_of_cycles):
		for f in fs:
			img = f(img, magnitude)

	return cvtColor(array(img), COLOR_RGB2BGR)


def __download_gif(url, filepath):
	for _ in range(5):
		try:
			urlretrieve(url, f'{filepath}.mp4')
			return 1
		except (HTTPError, URLError):
			sleep(1)
		except (OSError, UnboundLocalError):
			print("OSError while retrieving gif")
			return 0
	print("Quitting loop while retrieving gif")
	return 0