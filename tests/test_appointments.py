import unittest
import json
import sys
import os
from modules.Appointment import Appointment
from modules.Session import Session
from modules.Env import Env


class TestAppointments(unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		Env.set_mode(live=True)
		self.user_preferences = None
		if os.path.exists("user_preferences.json") and os.path.isfile("user_preferences.json"):
			with open("user_preferences.json") as f:
				self.user_preferences = json.loads(f.read())

	def perform_auth(self):
		if not self.user_preferences:
			sys.exit(1)
		session = Session(
			phone_number=self.user_preferences["MOBILE"], 
			secret=None, force=False)
		self.assertTrue(session.login() == True)
		session_data = session.export()
		return session, session_data

	def test_seek_area(self):
		if not self.user_preferences:
			sys.exit(1)
		session, session_data = self.perform_auth()
		appointment = Appointment(
			seek=0, pin_codes=["560029"], freq_s=30, mode_cron=True, token=session_data[0])
		appointment.seek_area()
		self.assertLess(appointment.last_status_code, 300)

	def test_seek(self):
		if not self.user_preferences:
			sys.exit(1)
		_, session_data = self.perform_auth()
		appointment = Appointment(
			seek=0, pin_codes=["560029"], freq_s=30, mode_cron=True, token=session_data[0])
		appointment.seek()
		self.assertLess(appointment.last_status_code, 300)
