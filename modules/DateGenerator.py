import time
from datetime import datetime

class DateGenerator:
	INTERVAL_24HR = 24*60*60
	seed_ts = None
	seed_obj = None
	seed_hr = None
	seed_min = None
	seed_sec = None

	@staticmethod
	def seed():
		DateGenerator.seed_ts = int(time.time())
		DateGenerator.seed_obj = datetime.fromtimestamp(DateGenerator.seed_ts)
		DateGenerator.seed_hr = int(DateGenerator.seed_obj.strftime("%H"))
		DateGenerator.seed_min = int(DateGenerator.seed_obj.strftime("%M"))
		DateGenerator.seed_sec = int(DateGenerator.seed_obj.strftime("%S"))

	@staticmethod
	def format_date_from_days(from_now = 0):
		ref_ts = DateGenerator.seed_ts + (from_now * DateGenerator.INTERVAL_24HR)
		date_obj = datetime.fromtimestamp(ref_ts)
		return date_obj.strftime("%d-%m-%Y")

	@staticmethod
	def get_seed_t():
		return [DateGenerator.seed_hr, DateGenerator.seed_min, DateGenerator.seed_sec]

	@staticmethod
	def get_now_t():
		time_now = int(time.time())
		time_now_obj = datetime.fromtimestamp(time_now)
		return [int(time_now_obj.strftime("%H")), int(time_now_obj.strftime("%M")), int(time_now_obj.strftime("%S"))]

	@staticmethod
	def get_ts():
		dateTimeObj = datetime.now()
		timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
		return timestampStr