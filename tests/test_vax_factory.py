import unittest
import json
from modules.Appointment import Appointment
from modules.VaxFactory import VaxFactory
from modules.Storage import Storage
from modules.Env import Env


class TestVaxFactory(unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()
		Env.set_mode(live=True)

	def reset(self):
		storage = Storage()
		storage.delete(VaxFactory.STORAGE_KEY)

	def test_import_boot(self):
		self.reset()
		VaxFactory.boot()
		appointment = Appointment(
			seek=2, pin_codes=["560029", "560034"], freq_s=30, mode_cron=True)
		with open("tests/test_vax_centers.json") as f:
			appointment.aggregate_centers(json.load(f))
		age_pool = VaxFactory.get_age_pools()
		vax_pool = VaxFactory.get_vaxes()
		center_pool = VaxFactory.get_centers()
		self.assertTrue(len(age_pool) == 2)
		self.assertTrue(len(vax_pool) >= 2)
		self.assertTrue(center_pool is not None and len(center_pool) >= 0)
