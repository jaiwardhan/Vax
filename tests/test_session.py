import unittest
import json
import sys
import os
from modules.Session import Session
from modules.Env import Env


class TestSession(unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		Env.set_mode(live=True)
		self.user_preferences = None
		if os.path.exists("user_preferences.json") and os.path.isfile("user_preferences.json"):
			with open("user_preferences.json") as f:
				self.user_preferences = json.loads(f.read())

	def test_login(self):
		if not self.user_preferences:
			sys.exit(1)
		session = Session(
			phone_number=self.user_preferences["MOBILE"],
			secret=None, force=False)
		self.assertTrue(session.login() == True)
		self.assertFalse(session.needs_refresh())
