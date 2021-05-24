from modules.Logger import Logger
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
    
    def test_logs(self):
        class T:
            def a(self):
                self.x = 1231
        t = T()
        Logger.log("asdf")
        Logger.log("asdfa", 1, "12312", {"a":1231}, ['asdf'], t)