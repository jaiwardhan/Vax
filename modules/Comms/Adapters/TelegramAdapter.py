from modules.Emojis import Emojis
import time
from modules.Config import APILoader
import telegram
from modules.Storage import Storage


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
            return
        elif (type(msg) is str or type(msg) is list) and \
                len(str(msg)) == 0:
            return
        if type(msg) is str:
            TelegramAdapter.bot.sendMessage(
                parse_mode='html', chat_id=self.CHANNEL_ID, text=msg)
        elif type(msg) is list:
            for each_message in msg:
                TelegramAdapter.bot.sendMessage(
                    parse_mode='html', chat_id=self.CHANNEL_ID, text=each_message)

    def post_time_sorter(self, a, b):
        if a["time"] > b["time"]:
            return -1
        return 1

    def read_otp_channel(self, timeout_s=30):
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
            Emojis.key + "Please send the login OTP here. Prepend 'otp' (Timeout %ds)" % (int(timeout_s)))

        end_time = record_time + int(timeout_s)
        while int(time.time()) < end_time:

            args = "?" + update_args["offset"] + \
                str(int(storage_data["last_update_id"])+1)
            resp = method(
                url=update_url+args
            )

            if resp and int(resp.status_code) < 300:
                otp = None
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
                        if "text" in post and str(post["text"]).lower().startswith("otp") and \
                                post["date"] > record_time:
                            posts.append({
                                "time": post["date"],
                                "text": str(post["text"]).lower()
                            })

                    # Sort and pick latest
                    if len(posts) > 0:
                        posts.sort(key=lambda b: b["time"], reverse=True)
                        latest = posts[0]
                        otp = str(latest["text"]).split(" ")[-1]

                    # Update back in cache and trigger write-through
                    storage_data["last_update_id"] = highest_update_id
                    storage.store(TelegramAdapter.STORAGE_KEY, storage_data)

                if otp is not None:
                    return otp
            time.sleep(0.5)
        return False
