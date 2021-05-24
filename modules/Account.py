import json
from modules.Appointment import AppointmentBooking
from modules.Config import APILoader, Network
from modules.Device import UserAgents
from modules.Logger import Logger


class Beneficiary:
	def __init__(self, data) -> None:
		self.id = data["beneficiary_reference_id"]
		self.name = data["name"]
		self.birth_year = data["birth_year"]
		self.gender = data["gender"]
		self.photo_id_type = data["photo_id_type"]
		self.comorbidity_ind = data["comorbidity_ind"]
		self.vaccination_status = data["vaccination_status"]
		self.dose1_date = data["dose1_date"]
		self.dose2_date = data["dose2_date"]
		self.appointments = []
		if "appointments" in data and len(data["appointments"]) > 0:
			for each_appointment_data in data["appointments"]:
				self.appointments.append(
					AppointmentBooking(each_appointment_data))


class Account:

	def __init__(self, session) -> None:
		self.beneficiaries = []
		self.beneficiaries_raw = []
		self.session = session
		base_url, method = APILoader.appointment_get_beneficiaries()
		headers = Network.headers_json()
		headers['User-Agent'] = UserAgents.android()
		headers['Authorization'] = "Bearer " + self.session.token
		resp = method(
			url=base_url,
			headers=headers
		)

		if int(resp.status_code) < 300:
			data = resp.json()
			self.beneficiaries_raw = [] if "beneficiaries" not in data else data["beneficiaries"]
			self.__parse_beneficiaries()
		else:
			Logger.log("Unable to get beneficiaries. ", resp.status_code)

	def __parse_beneficiaries(self):
		for each_beneficiary in self.beneficiaries_raw:
			self.beneficiaries.append(Beneficiary(each_beneficiary))

	def id_beneficiaries(self):
		return [each_beneficiary.id for each_beneficiary in self.beneficiaries]

	def short_desc_beneficiaries(self):
		return [{
			"id": each_beneficiary.id,
			"name": each_beneficiary.name,
			"birth_year": each_beneficiary.birth_year,
			"photo_id_type": each_beneficiary.photo_id_type
		} for each_beneficiary in self.beneficiaries]

	def book_appointment(self, dose_num, session_id, slot, beneficiaries):
		url, method = APILoader.appointment_get_schedule()
		headers = Network.headers_json()
		headers['User-Agent'] = UserAgents.android()
		headers['Authorization'] = "Bearer " + self.session.token
		payload = {
			"dose": int(dose_num),
			"session_id": session_id,
			"slot": slot,
			"beneficiaries": beneficiaries
		}
		resp = method(
			url=url,
			headers=headers,
			data=json.dumps(payload)
		)

		if int(resp.status_code) < 300:
			data = resp.json()
			appointment_id = data["appointment_id"]
			return appointment_id
		else:
			Logger.log("Unable to schedule an appointment. ", resp.status_code)
		return False
