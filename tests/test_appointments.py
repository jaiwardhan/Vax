import unittest
from modules.Appointment import Appointment
from modules.Session import Session
from modules.Env import Env


class TestAppointments(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        Env.set_mode(live=True)

    def perform_auth(self):
        session = Session(phone_number=8878550052, secret=None, force=False)
        self.assertTrue(session.login() == True)
        session_data = session.export()
        return session, session_data

    def test_seek_area(self):
        session, session_data = self.perform_auth()
        appointment = Appointment(
            seek=0, pin_codes=["560029"], freq_s=30, mode_cron=True, token=session_data[0])
        appointment.seek_area()
        self.assertLess(appointment.last_status_code, 300)

    def test_seek(self):
        _, session_data = self.perform_auth()
        appointment = Appointment(
            seek=0, pin_codes=["560029"], freq_s=30, mode_cron=True, token=session_data[0])
        appointment.seek()
        self.assertLess(appointment.last_status_code, 300)
