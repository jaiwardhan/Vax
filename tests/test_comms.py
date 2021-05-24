from modules.Logger import Logger
from modules.Env import Env
import os
import json
import unittest
from modules.Comms.CommController import CommController

class TestComms(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.capcom = None
        if os.path.exists("secrets_telegram_test.json") and os.path.isfile("secrets_telegram_test.json"):
            with open("secrets_telegram_test.json") as f:
                self.capcom = CommController(adapter=CommController.ADAPTER_TELEGRAM,
                    config=json.loads(f.read()))
            

    def test_telegram_otp(self):
        Env.set_mode(live=True)
        if self.capcom:
                otp = self.capcom.read_otp()
                self.assertEqual(otp, "6060")
    
    def test_logs(self):
        class T:
            def a(self):
                self.x = 1231
        t = T()
        Logger.log("asdf")
        Logger.log("asdfa", 1, "12312", {"a":1231}, ['asdf'], t)
    
    def test_hyperlink_text_copy(self):
        Env.set_mode(live=True)
        if self.capcom:
                _ = self.capcom.send("Test cd94ad7a-ac96-46ae-bb4d-3a658796073e 22-05-2021")
    
    def test_booking(self):
        Env.set_mode(live=True)
        if self.capcom:
                _ = self.capcom.send("Test cd94ad7a-ac96-46ae-bb4d-3a658796073e 22-05-2021")
                id, slot = self.capcom.read_booking_slot(timeout_s=20)
                self.assertEqual(id, "cd94ad7a-ac96-46ae-bb4d-3a658796073e")
                self.assertEqual(slot, "22-05-2021")