from io import BytesIO
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from PIL import Image
from telegram.ext import run_async


@run_async
def jpeg(bot, update, n=2, m=1):
	bio = BytesIO()
	bio.name = 'test.png'

	for _ in range(5):
		try:
			url = bot.get_file(update.message.reply_to_message.photo[::-1][0].file_id).file_path
			img = Image.open(BytesIO(urlopen(url).read()))
			for _ in range(m):
				w, h = img.size
				img = img.resize((int(w / n) if int(w / n) else 1, int(h / n) if int(h / n) else 1), Image.NEAREST)
			img.save(bio, 'PNG')
			bio.seek(0)
			bot.send_photo(
				update.message.chat_id,
				photo=bio,
				caption="Requested by %s, %d Cycle(s) of x%d Compression" % (update.message.from_user.first_name, m, n)
			)
			return

		except HTTPError or URLError:
			sleep(1)

		except OSError or UnboundLocalError or IndexError:
			return
