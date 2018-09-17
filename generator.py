from io import BytesIO
from os.path import join, dirname
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from PIL import Image
from PIL import ImageDraw, ImageFont
from telegram.ext.dispatcher import run_async

fonts = (
	ImageFont.truetype(join(dirname(__file__), 'Resources/raleway.ttf'), 32),
	ImageFont.truetype(join(dirname(__file__), 'Resources/raleway.ttf'), 24),
	ImageFont.truetype(join(dirname(__file__), 'Resources/raleway.ttf'), 16),
	ImageFont.truetype(join(dirname(__file__), 'Resources/raleway.ttf'), 12)
)


@run_async
def generate(bot, update, t: str, b: str):
	t = t.replace('\n', '')
	b = b.replace('\n', '')
	bio = BytesIO()
	bio.name = 'test.png'

	for _ in range(5):
		try:
			url = bot.get_file(update.message.reply_to_message.photo[::-1][0].file_id).file_path
			img = Image.open(BytesIO(urlopen(url).read()))
			w, h = img.width, img.height

			for f in range(3):
				draw = ImageDraw.Draw(img.copy())
				if __draw_top(draw, t, w, h, f) and __draw_bottom(draw, b, w, h, f):
					img.save(bio, 'PNG')
					bio.seek(0)
					bot.send_photo(
						update.message.chat_id,
						photo=bio,
						caption="Requested by %s" % update.message.from_user.first_name
					)

					# img.save('Resources/temp.jpg', 'JPEG')
					# upload_to_imgur(n)
					return

		except HTTPError or URLError:
			sleep(1)

		except OSError or UnboundLocalError or IndexError:
			return


def __draw_top(draw, t, w, h, f):
	t = t.strip()
	w90, w50, h5 = (w * 9) // 10, w // 2, h // 20
	wt, ht = fonts[f].getsize(t)

	if wt <= w90:
		__draw(draw, t, w50 - wt, h5, f)
		return True

	lines = __get_lines(t, w90, f)
	num_lines = len(lines)
	dims = [fonts[f].getsize(x) for x in lines]
	ws, hs = [x[0] for x in dims], [x[1] for x in dims]
	total = sum(hs)

	if total > (h // 4):
		return False

	y = h5
	for i in range(num_lines):
		__draw(draw, lines[i], w50 - ws[i], y, f)
		y += hs[i]

	return True


def __draw_bottom(draw, t, w, h, f):
	t = t.strip()
	w5, w90, w50, h95, h25, h50 = w // 20, (w * 9) // 10, w // 2, h // 20, h // 4, h // 2
	wt, ht = fonts[f].getsize(t)
	if wt <= w90:
		__draw(draw, t, w50 - wt, h95 - ht, f)
		return True

	lines = __get_lines(t, w90, f)
	num_lines = len(lines)
	dims = [fonts[f].getsize(x) for x in lines]
	ws, hs = [x[0] for x in dims], [x[1] for x in dims]
	total = sum(hs)

	if total > h25:
		return False

	y = h95
	for i in range(num_lines - 1, -1, -1):
		y -= hs[i]
		__draw(draw, lines[i], w50 - ws[i], y, f)

	return True


def __draw(draw, t, x, y, f):
	draw.text((x - 1, y), t, (0, 0, 0), font=fonts[f])
	draw.text((x + 1, y), t, (0, 0, 0), font=fonts[f])
	draw.text((x, y - 1), t, (0, 0, 0), font=fonts[f])
	draw.text((x, y + 1), t, (0, 0, 0), font=fonts[f])
	draw.text((x, y), t, (255, 255, 255), font=fonts[f])


def __get_lines(t, mw, f):
	w, _ = fonts[f].getsize(t)
	if w <= mw:
		return [t]
	t = t.split()
	for i in range(len(t), -1, -1):
		w, _ = fonts[f].getsize(" ".join(t[:i]))
		if w <= mw:
			return [" ".join(t[:i])] + __get_lines(" ".join(t[i:]), mw, f)
	for i in range(len(t[0]), -1, -1):
		w, _ = fonts[f].getsize("".join(t[:i]))
		if w <= mw:
			return ["".join(t[0][:i])] + __get_lines(" ".join(["".join(t[0][i:])] + t[1:]), mw, f)
