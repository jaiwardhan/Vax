import json
from modules.Logger import Logger
from os import stat
import time

import requests
from modules.DateGenerator import DateGenerator
from modules.VaxFactory import VaxFactory
from modules.Device import UserAgents
from modules.Config import APILoader, Network

class Appointment:

	URL_SEEK_PIN = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin"
	BANGALORE_URBAN = "265"
	BBMP = ""

	def __init__(self, seek = 3, pin_codes = ["560029"], 
		freq_s = 60, mode_cron = True, token = '',
		district_codes = ["265"]
		) -> None:
		self.attempts = 0
		self.days_seek = seek
		self.pin_codes = pin_codes
		self.freq_s = freq_s
		self.mode_cron = True if mode_cron else False
		self.token = token
		self.district_codes = district_codes

		self.operation_window_start_hr = 0
		self.operation_window_start_min = 0
		self.operation_window_end_hr = 23
		self.operation_window_end_min = 58

		self.last_status_code = 101

	def __cycle(self):
		if self.mode_cron:
			self.attempts += 1

	def operation_window(self, start_hr=0, start_min=0, end_hr=23, end_min=58):
		self.operation_window_start_hr = start_hr if start_hr >= 0 else 0
		self.operation_window_end_hr = end_hr if end_hr >= 0 else 23
		self.operation_window_start_min = start_min if start_min >= 0 else 0
		self.operation_window_end_min = end_min if end_min >= 0 else 58

	def can_continue(self):
		return (self.mode_cron and self.attempts < 1) or not self.mode_cron
	
	def reset(self):
		self.attempts = 0
	
	def __perform(self, perform, and_then = None):
		self.reset()
		DateGenerator.seed()

		while self.can_continue():
			perform()
			if and_then is not None:
				and_then()
				Logger.log("Sleeping for", self.freq_s)
				time.sleep(self.freq_s)
			self.__cycle()
	
	def __perform_seek(self):
		base_api_url, method = APILoader.appointment_by_pin()
		success = False
		for i in range(0, self.days_seek):
			date_to_check = DateGenerator.format_date_from_days(i)
			pincode = self.pin_codes[0]

			headers = Network.headers_json()
			headers['User-Agent'] = UserAgents.android()
			headers["Authorization"] = "Bearer " + self.token
			api_url = base_api_url + "?pincode=" + pincode + "&date=" + date_to_check

			resp = method(
				url=api_url, 
				headers=headers
			)
			self.last_status_code = int(resp.status_code)
			status = resp.status_code
			if resp:
				if int(status) < 300:
					success = True
				data = resp.json()
				Logger.log("(Pin API)", date_to_check, "[", status, "]", pincode, "::", data)
			else:
				Logger.log("(Pin API)", date_to_check, "[", status, "]", pincode, " X Failed", resp.content.decode())
			time.sleep(self.freq_s)
		return success
	
	def __perform_seek_area(self):
		base_api_url, method = APILoader.appointment_by_district()
		success = False
		for districts in self.district_codes:
			api_url = base_api_url + "?district_id=" + str(districts) + "&date=" + DateGenerator.format_date_from_days(0)
			headers = Network.headers_json()
			headers['User-Agent'] = UserAgents.android()
			headers['Authorization'] = "Bearer " + self.token
			resp = method(url=api_url, headers=headers)
			self.last_status_code = int(resp.status_code)
			if self.last_status_code < 300:
				success = True
				self.aggregate_centers(centers=json.loads(resp.content.decode()))
			else:
				Logger.log("(District Cal API)", resp.status_code, resp.content.decode())
		return success

	def seek(self):
		return self.__perform(self.__perform_seek)
	
	def seek_area(self, and_then = None):
		return self.__perform(self.__perform_seek_area, and_then)

	def aggregate_centers(self, centers):
		centers = centers if "centers" not in centers else centers["centers"]
		for each_center in centers:
			id = each_center["center_id"]
			name = each_center["name"]
			addr = each_center["address"]
			block = each_center["block_name"]
			pincode = each_center["pincode"]
			lati = each_center["lat"]
			longi = each_center["long"]
			sessions = each_center["sessions"]
			for each_session in sessions:
				session_id = each_session["session_id"]
				session_date = each_session["date"]
				min_age_limit = each_session["min_age_limit"]
				vax = each_session["vaccine"]
				cap_avail = each_session["available_capacity"]
				cap_avail_dose1 = each_session["available_capacity_dose1"]
				cap_avail_dose2 = each_session["available_capacity_dose2"]
				slots = each_session["slots"]
				VaxFactory.add_center(
					id, name, addr, block, pincode, lati, longi,
					session_id, session_date, min_age_limit, vax,
					cap_avail, cap_avail_dose1, cap_avail_dose2, slots
				)
