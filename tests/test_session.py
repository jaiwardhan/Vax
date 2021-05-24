import unittest
from modules.Session import Session
from modules.Env import Env


class TestSession(unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		Env.set_mode(live=True)

	def test_login(self):
		session = Session(phone_number=8878550052, secret=None, force=False)
		self.assertTrue(session.login() == True)
		self.assertFalse(session.needs_refresh())
