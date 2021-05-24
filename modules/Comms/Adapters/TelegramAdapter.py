import telegram
import time
from modules.Config import APILoader
from modules.Storage import Storage
from modules.Emojis import Emojis


class TelegramAdapter:
	STORAGE_KEY = "TELEGRAM_BOT"
	bot = None

	def __init__(self, config=None, reinit=False):
		if config is not None:
			if "PI_BOT_TOKEN" in config:
				self.BOT_TOKEN = config["PI_BOT_TOKEN"]
			if "PI_CHANNEL_ID" in config:
				self.CHANNEL_ID = config["PI_CHANNEL_ID"]
		if not reinit and TelegramAdapter.bot is not None:
			return
		TelegramAdapter.bot = telegram.Bot(token=self.BOT_TOKEN)

	def send(self, msg=''):
		if msg is None:
			return False
		elif (type(msg) is str or type(msg) is list) and \
				len(str(msg)) == 0:
			return False
		if type(msg) is str:
			TelegramAdapter.bot.sendMessage(
				parse_mode='html', chat_id=self.CHANNEL_ID, text=msg)
		elif type(msg) is list:
			for each_message in msg:
				TelegramAdapter.bot.sendMessage(
					parse_mode='html', chat_id=self.CHANNEL_ID, text=each_message)
		return True

	def post_time_sorter(self, a, b):
		if a["time"] > b["time"]:
			return -1
		return 1

	def read_from_channel(self, timeout_s, custom_message, startswith_pattern):
		record_time = int(time.time())
		update_url, update_args, method = APILoader.telegram_updates()
		update_url = update_url % (self.BOT_TOKEN)
		storage = Storage()
		storage_data, _ = storage.get(TelegramAdapter.STORAGE_KEY, {})
		args = ""
		last_update_id = 0
		if "last_update_id" in storage_data:
			last_update_id = int(storage_data["last_update_id"])
		else:
			storage_data["last_update_id"] = 0

		# Ready to trigger otp and wait
		self.send(
			custom_message + " (Timeout %ds)" % (int(timeout_s)))

		end_time = record_time + int(timeout_s)
		while int(time.time()) < end_time:

			args = "?" + update_args["offset"] + \
				str(int(storage_data["last_update_id"])+1)
			resp = method(
				url=update_url+args
			)

			if resp and int(resp.status_code) < 300:
				retrieved_data = None
				data = resp.json()
				if data["ok"] == True and len(data["result"]) > 0:
					results = data["result"]
					highest_update_id = last_update_id
					posts = []
					for each_result in results:
						highest_update_id = max(
							highest_update_id, int(each_result["update_id"]))
						if "channel_post" not in each_result:
							# Skip as this is not a channel post
							continue
						post = each_result["channel_post"]
						if "text" in post and str(post["text"]).lower().startswith(str(startswith_pattern).lower()) and \
								post["date"] > record_time:
							posts.append({
								"time": post["date"],
								"text": str(post["text"]).lower()
							})

					# Sort and pick latest
					if len(posts) > 0:
						posts.sort(key=lambda b: b["time"], reverse=True)
						latest = posts[0]
						retrieved_data = str(latest["text"])

					# Update back in cache and trigger write-through
					storage_data["last_update_id"] = highest_update_id
					storage.store(TelegramAdapter.STORAGE_KEY, storage_data)

				if retrieved_data is not None:
					return retrieved_data
			time.sleep(0.5)
		self.send(Emojis.fire + "Timed out!!")
		return False

	def read_otp_channel(self, timeout_s=30):
		data = self.read_from_channel(
			timeout_s=timeout_s,
			custom_message=Emojis.key + "Login OTP required: 'otp otp_number'.",
			startswith_pattern="otp"
		)
		if data and len(str(data)) > 0:
			_splits = data.split(" ")
			data_recons_splits = []
			for each_org_split in _splits:
				if len(each_org_split) > 0:
					data_recons_splits.append(each_org_split)

			data_filtered = " ".join(data_recons_splits)
			_, otp = data.split()
			return otp
		return False

	def read_booking_slot(self, timeout_s=10):
		data = self.read_from_channel(
			timeout_s=timeout_s,
			custom_message=Emojis.wait + "Awaiting booking confirmation: 'book session_id slot'.",
			startswith_pattern="book"
		)
		if data and len(str(data)) > 0:
			_splits = data.split(" ")
			data_recons_splits = []
			for each_org_split in _splits:
				if len(each_org_split) > 0:
					data_recons_splits.append(each_org_split)

			data_filtered = " ".join(data_recons_splits)
			_, center_id, slot = data.split()
			return center_id, slot
		return None, None
