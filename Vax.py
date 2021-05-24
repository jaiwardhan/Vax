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
		self.frequency_s = frequency_s,
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

	def me(self):
		if self.session.login():
			session_token, _, __ = self.session.export()
			self.appointment = Appointment(seek=3, pin_codes=self.pin_codes, freq_s=self.frequency_s,
										   mode_cron=self.mode_cron, token=session_token, district_codes=self.district_codes)
			self.appointment.seek_area()
			Logger.log(VaxFactory.get_vaxes())
			area_availabilities = self.view_controller.export_availabilities_external(
				availabilities=self.view_controller.get_by_age()
			)
			self.capcom.send(area_availabilities)
		else:
			self.capcom.send(Emojis.error + "Login Failed")


if __name__ == "__main__":
	vax = Vax(
		phone_number=9999988888,
		district_codes=["265"],
		pin_codes=["560029", "560034"],
		live_mode=True)

	# If running via command line it is assumed that a comm secrets file is
	# present.
	if os.path.exists("secrets_telegram.json") and os.path.isfile("secrets_telegram.json"):
		with open("secrets_telegram.json") as f:
			vax.configure(age=18, comm_config=json.loads(f.read()))
		vax.me()
	else:
		sys.exit(1)

# Import usage
# vax = Vax(...)
# vax.configure(age=18, ....)
# vax.me()