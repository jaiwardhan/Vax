import os
from modules.Comms.CommController import CommController
import time
from modules.Storage import Storage
import unittest
import json
from modules.Appointment import Appointment
from modules.VaxFactory import VaxFactory
from modules.Views import Views
from modules.Env import Env


class TestViews(unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		Env.set_mode(live=True)

	def test_availabilities(self):
		VaxFactory.boot()
		cli_view = Views(age=46)
		avails = cli_view.export_availabilities(cli_view.get_by_age())
		self.assertTrue(avails is not None)

	def test_availabilities_from_custom(self):
		storage = Storage()
		storage.delete(VaxFactory.STORAGE_KEY)
		VaxFactory.boot()
		appointment = Appointment(
			seek=2, pin_codes=["560029", "560034"], freq_s=30, mode_cron=True)
		with open("tests/test_vax_centers_for_18.json") as f:
			appointment.aggregate_centers(json.load(f))
		cli_view = Views(age=18)
		avails = cli_view.export_availabilities_external(cli_view.get_by_age())
		self.assertGreater(len(avails), 0)
		# To further relay this to your test channel, ensure
		# a secrets file related to your comm adapter is present.
		# In this case, it is assumed that secrets_telegram_test.json
		# is present to further proceed with the test.
		if os.path.exists("secrets_telegram_test.json") and os.path.isfile("secrets_telegram_test.json"):
			with open("secrets_telegram_test.json") as f:
				capcom = CommController(adapter=CommController.ADAPTER_TELEGRAM, 
					config=json.loads(f.read()))
				capcom.send(avails)
