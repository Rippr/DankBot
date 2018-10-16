from io import BytesIO
from os import remove
from os.path import abspath, isfile
from random import shuffle
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, urlretrieve

from PIL import Image, ImageEnhance, ImageOps
from cv2 import CHAIN_APPROX_NONE, CascadeClassifier, MORPH_CROSS, RETR_EXTERNAL, THRESH_BINARY, THRESH_BINARY_INV, \
	bitwise_and, boundingRect, dilate, findContours, getStructuringElement, threshold
from imageio import imread, get_reader, get_writer
from numba import jit
from numpy import abs, arcsin, arctan, array, copy, pi, sin, sqrt, square, sum
from numpy.random import normal, random
from pyimgur import Imgur
from telegram.ext.dispatcher import run_async


@run_async
def fry_image(update, url, n, args):
	e = 3 if args['high-fat'] else 1 if args['low-fat'] else 0 if args['no-fat'] else 2
	b = 0.75 if args['heavy'] else 0 if args['light'] else 0.45
	m = 4 if args['deep'] else 1 if args['shallow'] else 2
	name = update.message.from_user.first_name

	bio = BytesIO()
	bio.name = filename = '%s_%s_%s.png' % (update.message.chat_id, name, update.message.message_id)
	caption = "Requested by %s, %d Cycle(s)" % (name, n)

	success, img = __get_image(url)
	if success:
		img = __fry(img, n, e, b)

		fs = [__posterize, __sharpen, __increase_contrast, __colorize]
		for i in range(n):
			shuffle(fs)
			for f in fs:
				img = f(img, m)

		img.save(bio, 'PNG')
		bio.seek(0)
		update.message.reply_photo(photo=bio, caption=caption)
		img.save('temp/' + filename, 'PNG')
		__upload_to_imgur('temp/' + filename, caption)


@run_async
def fry_gif(update, url, n, args):
	e = 1.5 if args['high-fat'] else 1 if args['low-fat'] else 0
	b = 0.3 if args['heavy'] else 0.15 if args['light'] else 0
	m = 4 if args['deep'] else 1 if args['shallow'] else 2
	name = update.message.from_user.first_name

	gifbio = BytesIO()
	filename = '%s_%s_%s' % (update.message.chat_id, name, update.message.message_id)
	filepath = 'temp/' + filename
	gifbio.name = filename + '.gif'
	caption = "Requested by %s, %d Cycle(s)" % (name, n)

	success, reader = __get_gif_reader(url, filepath)
	if success:
		fps = reader.get_meta_data()['fps'] if 'fps' in reader.get_meta_data() else 30
		fs = [__posterize, __sharpen, __increase_contrast, __colorize]
		shuffle(fs)

		with get_writer(gifbio, format='gif', fps=fps) as writer:
			for i, img in enumerate(reader):
				img = Image.fromarray(img)
				img = __fry(img, n, e, b)

				for _ in range(n):
					for f in fs:
						img = f(img, m)

				bio = BytesIO()
				bio.name = filename + '.png'
				img.save(bio, 'PNG')
				bio.seek(0)

				image = imread(bio)
				writer.append_data(image)

		gifbio.seek(0)
		update.message.reply_animation(document=gifbio, caption=caption)
		remove(filepath + '.mp4')
		gifbio.seek(0)
		with open(filepath + '.gif', 'wb') as f:
			f.write(gifbio.read())
		__upload_to_imgur(filepath + '.gif', caption)


def __get_image(url):
	for _ in range(5):
		try:
			return 1, Image.open(BytesIO(urlopen(url).read()))
		except HTTPError or URLError:
			sleep(1)
		except OSError or UnboundLocalError or IndexError:
			return 0, None
	else:
		return 0, None


def __get_gif_reader(url, filepath):
	for _ in range(5):
		try:
			urlretrieve(url, filepath + '.mp4')
			return 1, get_reader(filepath + '.mp4')
		except HTTPError or URLError:
			sleep(1)
		except OSError or UnboundLocalError or IndexError:
			print("Error")
			return 0, None
	else:
		print("Quitting loop")
		return 0, None


@jit(fastmath=True)
def __fry(img, n, e, b):
	coords = __find_chars(img)
	# eyecoords = __find_eyes(img)
	if coords:
		img = __add_b(img, coords, e / 20)

	img = __add_emojis(img, n * e)
	# if eyecoords:
	# 	img = __add_flares(img, eyecoords)

	w, h = img.width - 1, img.height - 1
	for _ in range(n):
		if random(1)[0] <= b:
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
	gray = array(img.convert("L"))
	ret, mask = threshold(gray, 180, 255, THRESH_BINARY)
	image_final = bitwise_and(gray, gray, mask=mask)
	ret, new_img = threshold(image_final, 180, 255, THRESH_BINARY_INV)
	kernel = getStructuringElement(MORPH_CROSS, (3, 3))
	dilated = dilate(new_img, kernel, iterations=1)
	_, contours, hierarchy = findContours(dilated, RETR_EXTERNAL, CHAIN_APPROX_NONE)

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
	face_cascade = CascadeClassifier('Classifiers/haarcascade_frontalface_default.xml')
	eye_cascade = CascadeClassifier('Classifiers/haarcascade_eye.xml')
	gray = array(img.convert("L"))

	faces = face_cascade.detectMultiScale(gray, 1.3, 5)
	for (x, y, w, h) in faces:
		roi_gray = gray[y:y + h, x:x + w]
		eyes = eye_cascade.detectMultiScale(roi_gray)
		for (ex, ey, ew, eh) in eyes:
			coords.append((x + ex + ew / 2, y + ey + eh / 2))
	if len(coords) == 0:
		pass
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

	flare = Image.open('Frying/lazer.png')
	for coord in coords:
		tmp.paste(flare, (int(coord[0] - flare.size[0] / 2), int(coord[1] - flare.size[1] / 2)), flare)

	return tmp


@jit(fastmath=True)
def __add_b(img, coords, c):
	tmp = img.copy()

	b = Image.open('Frying/B.png')
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
		emoji = Image.open('Frying/%s.png' % i)
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
	client_id = 'ea567f3b9b802e5'
	client_key = 'f7021fab37102191bb3c2ec00f6b9541d0be86a4'
	access_token = 'f3fa0754bbd5f079938040834e4cf23d68fe7104'
	refresh_token = 'bcb50c6b9f8ce1343774aed388951e6126633b60'
	im = Imgur(client_id, client_key)

	if isfile(path):
		for _ in range(5):
			# noinspection PyBroadException
			try:
				full_path = abspath(path)
				im.access_token = access_token
				im.refresh_token = refresh_token
				im.upload_image(full_path, title=caption, album='pGXzpH0')
				remove(path)
				return
			except Exception:
				im.refresh_access_token()
				sleep(10)
