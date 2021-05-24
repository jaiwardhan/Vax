import requests
from modules.Env import Env


class Network:
	@staticmethod
	def headers_json():
		return {
			"Accept": "application/json",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
			"Content-Type": "application/json"
		}


class APILoader:

	BASE = {
		"demo": "https://api.demo.co-vin.in",
		"live": "https://cdn-api.co-vin.in"
	}

	APIs = {
		"otp": {
			"generate": {
				"api": "/api/v2/auth/public/generateOTP",
				"method": requests.post
			},
			"validate": {
				"api": "/api/v2/auth/public/confirmOTP",
				"method": requests.post
			}
		}
	}

	APPOINTMENTS = {
		"beneficiaries": {
			"api": "/v2/appointment/beneficiaries",
			"method": requests.get
		},
		"district": {
			"api": "/api/v2/appointment/sessions/calendarByDistrict",
			"method": requests.get
		},
		"pin": {
			"api": "/api/v2/appointment/sessions/findByPin",
			"method": requests.get
		},
		"schedule": {
			"api": "/v2/appointment/schedule",
			"method": requests.post
		}
	}

	TELEGRAM = {
		"update": {
			"base_url": "https://api.telegram.org",
			"api": "/bot%s/getUpdates",
			"args": {
						"offset": "offset="
			},
			"method": requests.get
		}
	}

	@staticmethod
	def get():
		return APILoader.BASE[Env.mode()]

	@staticmethod
	def otp_generate():
		ref = APILoader.APIs["otp"]["generate"]
		return APILoader.get() +\
			ref["api"], ref["method"]

	@staticmethod
	def otp_validate():
		ref = APILoader.APIs["otp"]["validate"]
		return APILoader.get() +\
			ref["api"], ref["method"]

	@staticmethod
	def appointment_by_pin():
		ref = APILoader.APPOINTMENTS["pin"]
		return APILoader.get() +\
			ref["api"], ref["method"]

	@staticmethod
	def appointment_by_district():
		ref = APILoader.APPOINTMENTS["district"]
		return APILoader.get() +\
			ref["api"], ref["method"]

	@staticmethod
	def appointment_get_beneficiaries():
		ref = APILoader.APPOINTMENTS["beneficiaries"]
		return APILoader.get() +\
			ref["api"], ref["method"]

	@staticmethod
	def appointment_get_schedule():
		ref = APILoader.APPOINTMENTS["schedule"]
		return APILoader.get() +\
			ref["api"], ref["method"]

	@staticmethod
	def telegram_updates():
		ref = APILoader.TELEGRAM["update"]
		return ref["base_url"] + ref["api"],\
			ref["args"], ref["method"]
