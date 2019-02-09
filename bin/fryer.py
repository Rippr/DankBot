from io import BytesIO
from os import environ, remove
from os.path import abspath, isfile, split as path_split
from random import shuffle
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, urlretrieve

from PIL import Image, ImageEnhance, ImageOps
from cv2 import CHAIN_APPROX_NONE, CascadeClassifier, MORPH_CROSS, RETR_EXTERNAL, THRESH_BINARY, THRESH_BINARY_INV, \
	bitwise_and, boundingRect, dilate, findContours, getStructuringElement, threshold, VideoWriter_fourcc, VideoWriter, \
	COLOR_BGR2RGB, cvtColor, COLOR_RGB2BGR, CAP_PROP_FPS
from imutils.video import FileVideoStream
from numba import jit
from numpy import arcsin, arctan, array, copy, pi, sin, sqrt, square, sum
from numpy.random import normal, random
from pyimgur import Imgur
from telegram.ext.dispatcher import run_async
from time import sleep

bin_path = path_split(abspath(__file__))[0]


@run_async
def fry_image(update, url, number_of_cycles, args):
	number_of_emojis = 3 if args['high-fat'] else 1 if args['low-fat'] else 0 if args['no-fat'] else 2
	bulge_probability = 0.75 if args['heavy'] else 0 if args['light'] else 0.45
	magnitude = 4 if args['deep'] else 1 if args['shallow'] else 2
	name = update.message.from_user.first_name

	bio = BytesIO()
	bio.name = filename = '%s_%s_%s.png' % (update.message.chat_id, name, update.message.message_id)
	caption = "Requested by %s, %d Cycle(s)" % (name, number_of_cycles)

	success, img = __get_image(url)
	if success:
		img = __fry(img, number_of_cycles, number_of_emojis, bulge_probability, args['chilli'])

		fs = [__posterize, __sharpen, __increase_contrast, __colorize]
		for _ in range(number_of_cycles):
			shuffle(fs)
			for f in fs:
				img = f(img, magnitude)

		img.save(bio, 'PNG')
		bio.seek(0)
		update.message.reply_photo(photo=bio, caption=caption)
		img.save(bin_path + '/temp/' + filename, 'PNG')
		__upload_to_imgur(bin_path + '/temp/' + filename, caption)


@run_async
def fry_gif(update, url, n, args):
	number_of_emojis = 1.5 if args['high-fat'] else 1 if args['low-fat'] else 0
	bulge_probability = 0.3 if args['heavy'] else 0.15 if args['light'] else 0
	magnitude = 4 if args['deep'] else 1 if args['shallow'] else 2
	name = update.message.from_user.first_name

	filename = '%s_%s_%s' % (update.message.chat_id, name, update.message.message_id)
	filepath = bin_path + '/temp/' + filename
	caption = "Requested by %s, %d Cycle(s)" % (name, n)
	output = bin_path + '/temp/out_' + filename + '.mp4'

	gifbio = BytesIO()
	gifbio.name = filename + '.gif'
	fs = [__posterize, __sharpen, __increase_contrast, __colorize]
	shuffle(fs)

	if __download_gif(url, filepath):
		fvs = FileVideoStream(filepath + '.mp4').start()
		frame1 = fvs.read()
		height, width, _ = frame1.shape

		try:
			fps = fvs.get(CAP_PROP_FPS)
		except:
			fps = 30
		out = VideoWriter(output, VideoWriter_fourcc(*'mp4v'), fps, (width, height))
		out.write(fry_frame(frame1, n, fs, number_of_emojis, bulge_probability, magnitude))

		while fvs.more():
			temp = fry_frame(fvs.read(), n, fs, number_of_emojis, bulge_probability, magnitude)
			out.write(temp)

		fvs.stream.release()
		out.release()
		_ = update.message.reply_animation(animation=open(output, 'rb'), caption=caption)
		remove(filepath + '.mp4')
		__upload_to_imgur(output, caption)


def __get_image(url):
	for _ in range(5):
		try:
			return 1, Image.open(BytesIO(urlopen(url).read()))
		except (HTTPError, URLError):
			sleep(1)
		except (OSError, UnboundLocalError):
			print("OSError while retreiving image")
			return 0, None
	print("Quitting loop while retreiving image")
	return 0, None


def __download_gif(url, filepath):
	for _ in range(5):
		try:
			urlretrieve(url, filepath + '.mp4')
			return 1
		except (HTTPError, URLError):
			sleep(1)
		except (OSError, UnboundLocalError):
			print("OSError while retreiving gif")
			return 0
	print("Quitting loop while retreiving gif")
	return 0


def fry_frame(frame, n, fs, e, b, m):
	# FIXME: Fails on the last frame for some reason.
	img = Image.fromarray(cvtColor(frame, COLOR_BGR2RGB))
	img = __fry(img, n, e, b)
	for _ in range(n):
		for f in fs:
			img = f(img, m)
	return cvtColor(array(img), COLOR_RGB2BGR)


@jit(fastmath=True)
def __fry(img, number_of_cycles, number_of_emojis, bulge_probability, laser):
	if laser:
		eyecoords = __find_eyes(img)
		if eyecoords:
			img = __add_flares(img, eyecoords)

	# coords = __find_chars(img)

	# if coords:
	# 	img = __add_b(img, coords, e / 20)

	img = __add_emojis(img, number_of_cycles * number_of_emojis)

	w, h = img.width - 1, img.height - 1
	for _ in range(number_of_cycles):
		if random(1)[0] <= bulge_probability:
			w *= random(1)
			h *= random(1)
			r = int(((img.width + img.height) / 10) * (random(1)[0] + 1))
			img = __add_bulge(
				img,
				array([int(w), int(h)]),
				r,
				2 + random(2)[0],
				6 + random(2)[0],
				1.3 + random(1)[0]
			)
	return img


@jit(fastmath=True)
def __find_chars(img):
	# Convert image to B&W
	gray = array(img.convert("L"))

	# Convert image to binary
	_, mask = threshold(gray, 180, 255, THRESH_BINARY)
	image_final = bitwise_and(gray, gray, mask=mask)
	_, new_img = threshold(image_final, 180, 255, THRESH_BINARY_INV)

	# Idk
	kernel = getStructuringElement(MORPH_CROSS, (3, 3))
	dilated = dilate(new_img, kernel, iterations=1)
	# FIXME
	_, contours, _ = findContours(dilated, RETR_EXTERNAL, CHAIN_APPROX_NONE)

	coords = []
	for contour in contours:
		# get rectangle bounding contour
		[x, y, w, h] = boundingRect(contour)
		# ignore large chars (probably not chars)
		if w > 70 and h > 70:
			continue
		coords.append((x, y, w, h))
	return coords


@jit(fastmath=True)
def __find_eyes(img):
	coords = []
	face_cascade = CascadeClassifier(bin_path + '/Resources/haarcascade_frontalface_default.xml')
	eye_cascade = CascadeClassifier(bin_path + '/Resources/haarcascade_eye.xml')
	gray = array(img.convert("L"))

	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	for (x, y, w, h) in faces:
		roi_gray = gray[y:y + h, x:x + w]
		eyes = eye_cascade.detectMultiScale(roi_gray)
		for (ex, ey, ew, eh) in eyes:
			coords.append((x + ex + ew / 2, y + ey + eh / 2))
	return coords


@jit(fastmath=True)
def __posterize(img, p):
	return ImageOps.posterize(
		img,
		4 if p == 4 else 6 if p == 1 else 5
	)


@jit(fastmath=True)
def __sharpen(img, p):
	return ImageEnhance.Sharpness(img).enhance((img.width * img.height * p / 3200) ** 0.4)


@jit(fastmath=True)
def __increase_contrast(img, p):
	return ImageEnhance.Contrast(img).enhance(normal(1.8, 0.8) * p / 2)


@jit(fastmath=True)
def __colorize(img, p):
	return ImageEnhance.Color(img).enhance(normal(2.5, 1) * p / 2)


@jit(fastmath=True)
def __add_flares(img, coords):
	tmp = img.copy()

	flare = Image.open(bin_path + '/Frying/lazer.png')
	for coord in coords:
		tmp.paste(flare, (int(coord[0] - flare.size[0] / 2), int(coord[1] - flare.size[1] / 2)), flare)

	return tmp


@jit(fastmath=True)
def __add_b(img, coords, c):
	tmp = img.copy()

	b = Image.open(bin_path + '/Frying/B.png')
	for coord in coords:
		if random(1)[0] < c:
			resized = b.copy()
			resized.thumbnail((coord[2], coord[3]), Image.ANTIALIAS)
			tmp.paste(resized, (int(coord[0]), int(coord[1])), resized)

	return tmp


@jit(fastmath=True)
def __add_emojis(img, m):
	emojis = ['100', 'OK', 'laugh', 'fire', 'think']
	tmp = img.copy()

	for i in emojis:
		emoji = Image.open(bin_path + '/Frying/%s.png' % i)
		for _ in range(int(random(1)[0] * m)):
			coord = random(2) * array([img.width, img.height])
			size = int((img.width / 10) * (random(1)[0] + 1)) + 1
			theta = random(1)[0] * 360

			resized = emoji.copy()
			resized = resized.rotate(theta)
			resized.thumbnail((size, size), Image.ANTIALIAS)
			tmp.paste(resized, (int(coord[0]), int(coord[1])), resized)

	return tmp


@jit(fastmath=True)
def __add_bulge(img: Image.Image, f, r, a, h, ior):
	"""
	Creates a bulge like distortion to the image

	:param img: The Image
	:type img: PIL.Image
	:param f: Numpy Array with Coordinates of Centre of Bulge
	:type f: numpy.array
	:param r: Radius of Bulge
	:type r: int
	:param a: Flatness: Spherical -> 1, Flat -> > 1
	:type a: int
	:param h: Height of Bulge
	:type h: int
	:param ior: Index of Refraction of Bulge Material
	:type ior: float
	:return: The Bulged Image
	:rtype: PIL.Image
	"""

	width = img.width
	height = img.height
	# noinspection PyTypeChecker
	img_data = array(img)

	if width * height > 9000000:
		return img

	# determine range of pixels to be checked (square enclosing bulge), max exclusive
	x_min = int(f[0] - r)
	if x_min < 0:
		x_min = 0
	x_max = int(f[0] + r)
	if x_max > width:
		x_max = width
	y_min = int(f[1] - r)
	if y_min < 0:
		y_min = 0
	y_max = int(f[1] + r)
	if y_max > height:
		y_max = height

	# make sure that bounds are int and not np array
	if isinstance(x_min, type(array([]))):
		x_min = x_min[0]
	if isinstance(x_max, type(array([]))):
		x_max = x_max[0]
	if isinstance(y_min, type(array([]))):
		y_min = y_min[0]
	if isinstance(y_max, type(array([]))):
		y_max = y_max[0]

	# array for holding bulged image
	bulged = copy(img_data)
	for y in range(y_min, y_max):
		for x in range(x_min, x_max):
			ray = array([x, y])

			# find the magnitude of displacement in the xy plane between the ray and focus
			s = sqrt(sum(square(ray - f)))

			# if the ray is in the centre of the bulge or beyond the radius it doesn't need to be modified
			if 0 < s < r:
				# slope of the bulge relative to xy plane at (x, y) of the ray
				m = -s / (a * sqrt(r ** 2 - s ** 2))

				# find the angle between the ray and the normal of the bulge
				theta = pi / 2 + arctan(1 / m)

				# find the magnitude of the angle between xy plane and refracted ray using snell's law
				# s >= 0 -> m <= 0 -> arctan(-1/m) > 0, but ray is below xy plane so we want a negative angle
				# arctan(-1/m) is therefore negated
				phi = abs(arctan(1 / m) - arcsin(sin(theta) / ior))

				# find length the ray travels in xy plane before hitting z=0
				k = (h + (sqrt(r ** 2 - s ** 2) / a)) / sin(phi)

				# find intersection point
				normalized = (f - ray) / sqrt(sum(square(f - ray)))
				intersect = ray + normalized * k

				# assign pixel with ray's coordinates the colour of pixel at intersection
				if 0 < intersect[0] < width - 1 and 0 < intersect[1] < height - 1:
					bulged[y][x] = img_data[int(intersect[1])][int(intersect[0])]
				else:
					bulged[y][x] = [0, 0, 0]
			else:
				bulged[y][x] = img_data[y][x]
	img = Image.fromarray(bulged)
	return img


@run_async
def __upload_to_imgur(path, caption):
	client_id = environ.get('IMGUR_CLIENT_ID')
	client_key = environ.get('IMGUR_CLIENT_KEY')
	access_token = environ.get('IMGUR_ACCESS_TOKEN')
	refresh_token = environ.get('IMGUR_REFRESH_TOKEN')
	im = Imgur(client_id, client_key)

	if isfile(path):
		for _ in range(5):
			# noinspection PyBroadException
			try:
				full_path = abspath(path)
				im.access_token = access_token
				im.refresh_token = refresh_token
				im.upload_image(full_path, title=caption, album=environ.get('IMGUR_ALBUM'))
				remove(path)
				return
			except Exception:
				im.refresh_access_token()
				sleep(10)
