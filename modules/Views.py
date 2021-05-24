from modules.VaxFactory import VaxFactory
from modules.Emojis import Emojis


class Availabilities:

	class Availability:
		def __init__(self, data) -> None:
			self.id = data["center"].id
			self.name = data["center"].name
			self.locations = data["center"].location.pin()
			self.pincode = data["center"].pincode
			self.vax = data["session"].vax
			self.session_id = data["session"].session_id
			self.session_date = data["session"].session_date
			self.min_age = data["session"].min_age_limit
			self.available = data["session"].cap_avail
			self.available_dose1 = data["session"].cap_avail_dose1
			self.available_dose2 = data["session"].cap_avail_dose2
			self.slots = data["session"].slots

		def export(self):
			return {
				"id": self.id,
				"name": self.name,
				"locations": self.locations,
				"vax": self.vax,
				"pincode": self.pincode,
				"min_age": self.min_age,
				"available": self.available,
				"available_dose1": self.available_dose1,
				"available_dose2": self.available_dose2,
				"slots": self.slots,
				"session_date": self.session_date,
				"session_id": self.session_id
			}

	def __init__(self) -> None:
		self.avails = []

	def add(self, data):
		self.avails.append(Availabilities.Availability(data))

	def export(self):
		return [e.export() for e in self.avails]


class Views:

	# Github issue: https://github.com/cowinapi/developer.cowin/issues/7
	ENABLE_PRECISE_LOCATION = False
	BATCH_EXPORT_LIMIT = 5

	def __init__(self, age, dose=0, vax_pref="COVAXIN") -> None:
		self.age = age
		self.vax_pref = vax_pref
		self.dose = dose

	def get_by_vax(self):
		"""Gets the most prefferred vax view irrespective of the age

		Returns:
				list: A list of dicts containing center and session information
		"""

		availabilities = []
		if self.vax_pref not in VaxFactory.vax_pool.keys():
			return availabilities
		for vax_center_id in VaxFactory.vax_pool[self.vax_pref].keys():
			session_data = VaxFactory.vax_pool[self.vax_pref][vax_center_id]["sessions"]
			session_data = session_data if session_data else []
			for each_session in session_data:
				if self.vax_pref and each_session.vax != self.vax_pref:
					continue
				if (self.dose == 0 and each_session.cap_avail_dose1 == 0) or\
						(self.dose != 0 and each_session.cap_avail_dose2 == 0):
					continue
				# Qualifies
				availabilities.append({
					"center": VaxFactory.get_center(vax_center_id),
					"session": each_session
				})
		return availabilities

	def get_by_age(self):
		"""Gets the age qualified vax view irrespective of vax preference

		Returns:
				list: A list of dicts containing center and session information
		"""
		availabilities = []
		for vax_center_id in VaxFactory.pool.keys():
			session_data = VaxFactory.pool[vax_center_id].session_data
			session_data = session_data if session_data else []
			for each_session in session_data:
				if self.age >= int(each_session.min_age_limit):
					if (self.dose == 0 and each_session.cap_avail_dose1 == 0) or\
							(self.dose != 0 and each_session.cap_avail_dose2 == 0):
						continue
					# Qualifies
					availabilities.append({
						"center": VaxFactory.get_center(vax_center_id),
						"session": each_session
					})
		return availabilities

	def get_most_prefferred(self):
		"""Gets the most prefferred view where both age and preferred vax criteria are met

		Returns:
				list: A list of dicts containing center and session information
		"""
		availabilities = []
		if self.vax_pref not in VaxFactory.vax_pool.keys():
			return availabilities
		for vax_center_id in VaxFactory.vax_pool[self.vax_pref].keys():
			session_data = VaxFactory.vax_pool[self.vax_pref][vax_center_id]["sessions"]
			session_data = session_data if session_data else []
			for each_session in session_data:
				if self.vax_pref and each_session.vax != self.vax_pref:
					continue
				if self.age >= int(each_session.min_age_limit):
					if (self.dose == 0 and each_session.cap_avail_dose1 == 0) or\
							(self.dose != 0 and each_session.cap_avail_dose2 == 0):
						continue
					# Qualifies
					availabilities.append({
						"center": VaxFactory.get_center(vax_center_id),
						"session": each_session
					})
		return availabilities

	def export_availabilities(self, availabilities):
		availabilities_o = Availabilities()
		for each_availability in availabilities:
			availabilities_o.add(each_availability)
		return availabilities_o.export()

	def export_availabilities_external(self, availabilities):
		availabilities_o = Availabilities()
		for each_availability in availabilities:
			availabilities_o.add(each_availability)
		exportable_data = availabilities_o.export()
		if len(exportable_data) == 0:
			return None
		msgs = []

		# Batch messages if length > BATCH_EXPORT_LIMIT
		batch_iteration = 0
		for each_exportable_availability in exportable_data:
			msg = "\n" + "Center: " + each_exportable_availability["name"]
			msg += "\n" + "pincode: " + \
				str(each_exportable_availability["pincode"])
			msg += "\n" + "Vax: " + str(each_exportable_availability["vax"])
			msg += "\n" + "Age: " + \
				str(each_exportable_availability["min_age"])
			msg += "\n" + "Your Dose #" + str(self.dose+1) + ", available: " +\
				str(each_exportable_availability["available_dose1"]) if self.dose == 0 \
				else str(each_exportable_availability["available_dose2"])
			session_date = str(each_exportable_availability["session_date"])
			session_id = str(each_exportable_availability["session_id"])
			msg += "\n" + "Slot Date: " + session_date
			msg += "\n" + "Session ID: " + session_id

			if Views.ENABLE_PRECISE_LOCATION:
				locations = each_exportable_availability["locations"] if "locations" in each_exportable_availability\
					else []
				if len(locations) > 0:
					msg += "\n Locations:"
					msg += "\n -- <a href='%s'>Google Maps</a>" % (
						locations[0])
					msg += "\n -- <a href='%s'>Apple Maps</a>" % (locations[1])
					msg += "\n -- <a href='%s'>Bing Maps</a>" % (locations[2])

			# Include session id again so that it can be easily copied with slot in one go
			slots = each_exportable_availability["slots"] if "slots" in each_exportable_availability\
				else []
			msg += "\n" + "Slots:" if len(slots) > 0 else ""
			for each_slot in slots:
				msg += "\n" + " - (id, time): " + \
					session_id + " " + str(each_slot)
			msg += "\n -------------- "

			batch_iteration += 1
			if batch_iteration <= Views.BATCH_EXPORT_LIMIT:
				if len(msgs) == 0:
					msgs.append(
						Emojis.vax + " Vax availability detected in accordance to your preferences:" + "\n")
				msgs[-1] += msg
			else:
				msgs.append(
					Emojis.vax + " Vax availability detected in accordance to your preferences:" + "\n")
				msgs[-1] += msg
				batch_iteration = 0
		return msgs[0] if len(msgs) == 1 else msgs
