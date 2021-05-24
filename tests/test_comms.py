from modules.Env import Env
import os
import json
import unittest
from modules.Comms.CommController import CommController

class TestComms(unittest.TestCase):

    def test_telegram_otp(self):
        Env.set_mode(live=True)
        if os.path.exists("secrets_telegram_test.json") and os.path.isfile("secrets_telegram_test.json"):
            with open("secrets_telegram_test.json") as f:
                capcom = CommController(adapter=CommController.ADAPTER_TELEGRAM,
                    config=json.loads(f.read()))
                otp = capcom.read_otp()
                self.assertEqual(otp, "6060")
