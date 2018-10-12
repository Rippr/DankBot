import configparser
import json
from urllib.parse import urlencode
from urllib.request import urlopen

# standard app engine imports
# from google.appengine.api import urlfetch
import webapp2

BASE_URL = ""
TOKEN = ""
HOOK_TOKEN = ""
PROJECT_ID = ""

# Lambda functions to parse updates from Telegram
getText = lambda update: update["message"]["text"]
getChatID = lambda update: update["message"]["chat"]["id"]
getName = lambda update: update["message"]["from"]["first_name"]

# Accepted commands
commands = ["/weather", "/fact", "/mirror", "/fortune", "/trivia"]


# Read settings from configuration file
def parse_config():
	global BASE_URL, TOKEN, HOOK_TOKEN, PROJECT_ID

	c = configparser.ConfigParser()
	c.read("config.ini")
	TOKEN = c.get("Settings", "TOKEN")
	BASE_URL = "https://api.telegram.org/bot" + TOKEN + "/"

	HOOK_TOKEN = c.get("Settings", "HOOK_TOKEN")
	PROJECT_ID = c.get("Settings", "PROJECT_ID")


# Set requests timeout (default is 15)
def set_timeout(numSec=60):
	# urlfetch.set_default_fetch_deadline(numSec)
	pass


# Deserialise object and serialise it to JSON formatted string
def format_resp(obj):
	parsed = json.load(obj)
	return json.dumps(parsed, indent=4, sort_keys=True)


# Make a request and get JSON response
def make_request(url):
	r = urlopen(url)
	resp = json.load(r)
	return resp


# Build a one-time keyboard for on-screen options
def build_keyboard(items):
	keyboard = [[{"text": item}] for item in items]
	replyKeyboard = {"keyboard": keyboard, "one_time_keyboard": True}
	return json.dumps(replyKeyboard)


# Send URL-encoded message to chat id
def send_message(text, chatId, interface=None):
	params = {
		"chat_id": str(chatId),
		"text": text.encode("utf-8"),
		"parse_mode": "Markdown",
	}
	if interface:
		params["reply_markup"] = interface

	urlopen(BASE_URL + "sendMessage", urlencode(params)).read()


# Return basic information about the bot
class MeHandler(webapp2.RequestHandler):
	def get(self):
		set_timeout()
		parse_config()

		url = BASE_URL + "getMe"
		respBuf = urlopen(url)

		self.response.headers["Content-Type"] = "text/plain"
		self.response.write(format_resp(respBuf))


# Get information about webhook status
class GetWebhookHandler(webapp2.RequestHandler):
	def get(self):
		set_timeout()
		parse_config()

		url = BASE_URL + "getWebhookInfo"
		respBuf = urlopen(url)

		self.response.headers["Content-Type"] = "text/plain"
		self.response.write(format_resp(respBuf))


# Set a webhook url for Telegram to POST to
class SetWebhookHandler(webapp2.RequestHandler):
	def get(self):
		set_timeout()
		parse_config()

		hookUrl = "https://%s.appspot.com/TG%s" % (PROJECT_ID, HOOK_TOKEN)
		respBuf = urlopen(BASE_URL + "setWebhook", urlencode({
			"url": hookUrl
		}))
		self.response.headers["Content-Type"] = "text/plain"
		self.response.write(format_resp(respBuf))


# Remove webhook integration
class DeleteWebhookHandler(webapp2.RequestHandler):
	def get(self):
		set_timeout()
		parse_config()

		url = BASE_URL + "deleteWebhook"
		respBuf = urlopen(url)

		self.response.headers["Content-Type"] = "text/plain"
		self.response.write(format_resp(respBuf))


# Handler for the webhook, called by Telegram
class WebhookHandler(webapp2.RequestHandler):
	def post(self):
		set_timeout()
		parse_config()

		if HOOK_TOKEN not in self.request.url:
			# Not coming from Telegram
			return

		body = json.loads(self.request.body)

		chatId = getChatID(body)

		try:
			text = getText(body)
		except Exception:
			return

		if text == "/start":
			keyboard = build_keyboard(commands)
			send_message("Hello %s! Why not try the commands below:" % getName(body), chatId, keyboard)


app = webapp2.WSGIApplication([
	('/me', MeHandler),
	('/set_webhook', SetWebhookHandler),
	('/get_webhook', GetWebhookHandler),
	('/del_webhook', DeleteWebhookHandler),
	(r'/TG.*', WebhookHandler),
], debug=True)
