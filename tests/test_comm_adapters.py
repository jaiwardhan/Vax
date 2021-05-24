import unittest
import json
import os

from modules.Comms.CommController import CommController

class TestCommAdapters(unittest.TestCase):

	def test_telegram(self):
		# Runs only if secret_telegram_test.json is present
		if os.path.exists("secrets_telegram_test.json") and os.path.isfile("secrets_telegram_test.json"):
			with open("secrets_telegram_test.json") as f:
				capcom = CommController(
					adapter=CommController.ADAPTER_TELEGRAM,
					config=json.loads(f.read())
				)
				capcom.send("Jitter Chitter from Vax tests")
				found = input("Did you recv the message? (y/*): ")
				found = str(found).lower()
				self.assertEqual(found, "y")