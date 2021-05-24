from modules.Logger import Logger
from modules.VaxFactory import VaxFactory
import os
import sys
import json
from modules.Comms.CommController import CommController
from modules.Appointment import Appointment
from modules.Session import Session
from modules.Emojis import Emojis
from modules.Views import Views
from modules.Env import Env


class Vax:

	def __init__(self, phone_number,
				 district_codes, pin_codes,
				 frequency_s=30, mode_cron=True, live_mode=False) -> None:

		self.phone_number = phone_number
		self.district_codes = district_codes
		self.pin_codes = pin_codes
		self.frequency_s = frequency_s
		self.mode_cron = mode_cron
		Env.set_mode(live=live_mode)
		VaxFactory.boot()

	def configure(self, age, comm_config, commAdapter=CommController.ADAPTER_TELEGRAM):
		self.age = age
		self.comm_config = comm_config
		self.capcom = CommController(
			adapter=commAdapter, config=self.comm_config)
		self.view_controller = Views(self.age)
		self.session = Session(
			phone_number=self.phone_number, secret=None, capcom=self.capcom
		)

	def aggregate_and_send(self):
		Logger.log(VaxFactory.get_vaxes())
		area_availabilities = self.view_controller.export_availabilities_external(
			availabilities=self.view_controller.get_by_age()
		)
		self.capcom.send(area_availabilities)

	def me(self):
		if self.session.login():
			session_token, _, __ = self.session.export()
			self.appointment = Appointment(seek=3, pin_codes=self.pin_codes, freq_s=self.frequency_s,
										   mode_cron=self.mode_cron, token=session_token, district_codes=self.district_codes)
			self.appointment.seek_area(and_then=self.aggregate_and_send)
		else:
			self.capcom.send(Emojis.error + "Login Failed")


if __name__ == "__main__":
	vax = None
	user_preferences = None
	if os.path.exists("user_preferences.json") and os.path.isfile("user_preferences.json"):
		with open("user_preferences.json") as f:
			user_preferences = json.loads(f.read())
			vax = Vax(
				phone_number=int(user_preferences["MOBILE"]),
				district_codes=user_preferences["DIST_CODES"],
				pin_codes=user_preferences["PIN_CODES"],
				live_mode=True, mode_cron=False,
				frequency_s = 10
			)

	if vax is not None and user_preferences is not None and \
		os.path.exists("secrets_telegram.json") and os.path.isfile("secrets_telegram.json"):
		with open("secrets_telegram.json") as f:
			vax.configure(age=int(user_preferences["AGE"]), comm_config=json.loads(f.read()))
		vax.me()
	else:
		sys.exit(1)

# Import usage
# vax = Vax(...)
# vax.configure(age=18, ....)
# vax.me()