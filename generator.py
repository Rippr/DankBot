from io import BytesIO
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from PIL import Image
from telegram.ext.dispatcher import run_async


@run_async
def nuke(bot, update, n):
	bio = BytesIO()
	bio.name = 'test.png'

	for _ in range(5):
		try:
			url = bot.get_file(update.message.reply_to_message.photo[::-1][0].file_id).file_path
			img = Image.open(BytesIO(urlopen(url).read()))

			# for i in range(n):
			# 	img = fry(img)

			img.save(bio, 'PNG')
			bio.seek(0)
			bot.send_photo(
				update.message.chat_id,
				photo=bio,
				caption="Requested by %s, %d Cycle(s)" % (update.message.from_user.first_name, n)
			)
			# img.save('Resources/temp.jpg', 'JPEG')
			# upload_to_imgur(n)
			# return

		except HTTPError or URLError:
			sleep(1)

		except OSError or UnboundLocalError or IndexError:
			return
