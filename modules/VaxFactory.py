import json
from modules.Storage import Storage


class VaxSession:
	def __init__(self, session_id, session_date,
				 min_age_limit, vax, cap_avail,
				 cap_avail_dose1, cap_avail_dose2, slots) -> None:
		self.session_id = session_id
		self.session_date = session_date
		self.min_age_limit = min_age_limit
		self.vax = vax
		self.cap_avail = cap_avail
		self.cap_avail_dose1 = cap_avail_dose1
		self.cap_avail_dose2 = cap_avail_dose2
		self.slots = slots

	def export(self):
		return {
			"session_id": self.session_id,
			"session_date": self.session_date,
			"min_age_limit": self.min_age_limit,
			"vax": self.vax,
			"cap_avail": self.cap_avail,
			"cap_avail_dose1": self.cap_avail_dose1,
			"cap_avail_dose2": self.cap_avail_dose2,
			"slots": self.slots
		}

	@staticmethod
	def data_import(data):
		return VaxSession(
			data["session_id"],
			data["session_date"],
			data["min_age_limit"],
			data["vax"],
			data["cap_avail"],
			data["cap_avail_dose1"],
			data["cap_avail_dose2"],
			data["slots"]
		)


class VaxLocation:
	def __init__(self, lati, longi) -> None:
		self.lati = lati
		self.longi = longi

	def export(self):
		return {
			"lati": self.lati,
			"longi": self.longi
		}

	@staticmethod
	def data_import(data):
		return VaxLocation(data["lati"], data["longi"])

	def pin(self, google=True, apple=True, bing=True):
		pins = []
		if google:
			pins.append("https://www.google.com/maps/search/?api=1&query=" +
						str(self.lati) + "," + str(self.longi))
		if apple:
			pins.append("http://maps.apple.com/?sll=" +
						str(self.lati) + "," + str(self.longi) + "&z=10&t=s")
		if bing:
			pins.append("https://bing.com/maps/default.aspx?cp=" +
						str(self.lati) + "~" + str(self.longi))

		return self.pin(google=True, apple=False, bing=False) if len(pins) == 0 else pins


class VaxCenter:
	def __init__(self, id, name, addr, block, pincode,
				 location, sessions=None) -> None:
		self.id = id
		self.name = name
		self.addr = addr
		self.block = block
		self.pincode = pincode
		self.location = location
		self.session_data = []
		self.session_data_sig = {}
		if sessions:
			self.import_sessions(sessions)

	def import_sessions(self, sessions):
		for each_session in sessions:
			vax_session = VaxSession.data_import(each_session)
			self.session_data.append(vax_session)
			self.session_data_sig[vax_session.session_id] = len(
				self.session_data)-1

	def add_session(self, session_id, session_date,
					min_age_limit, vax, cap_avail,
					cap_avail_dose1, cap_avail_dose2, slots):

		# A session data might change if it gets updated
		# hence delete the old and update new
		if session_id in self.session_data_sig:
			idx = self.session_data_sig[session_id]
			self.session_data = self.session_data[:idx] + \
				self.session_data[idx+1:]
			del self.session_data_sig[session_id]

		vax_session = VaxSession(
			session_id, session_date,
			min_age_limit, vax, cap_avail,
			cap_avail_dose1, cap_avail_dose2,
			slots
		)
		self.session_data.append(vax_session)
		self.session_data_sig[session_id] = len(self.session_data)-1
		return vax_session

	def export_sessions(self):
		return [c.export() for c in self.session_data]

	def export(self):
		return {
			"id": self.id,
			"name": self.name,
			"addr": self.addr,
			"block": self.block,
			"pincode": self.pincode,
			"location": self.location.export(),
			"sessions": self.export_sessions()
		}

	@staticmethod
	def data_import(data):
		return VaxCenter(
			data["id"],
			data["name"],
			data["addr"],
			data["block"],
			data["pincode"],
			VaxLocation.data_import(data["location"]),
			data["sessions"]
		)


class VaxFactory:

	pool = {}
	age_pool = {}
	pin_code = {}
	vax_pool = {}
	STORAGE_KEY = "VAX_FACTORY"
	storage = Storage()

	@staticmethod
	def find_or_create(id, name, addr, block, pincode,
					   lati, longi):
		if id not in VaxFactory.pool:
			VaxFactory.pool[id] = VaxCenter(
				id=id, name=name, addr=addr, block=block,
				pincode=pincode, location=VaxLocation(lati, longi)
			)
		return VaxFactory.pool[id]

	@staticmethod
	def add_age_pool(min_age, vax_center, session):
		if min_age not in VaxFactory.age_pool:
			VaxFactory.age_pool[min_age] = {}
		if vax_center.id not in VaxFactory.age_pool[min_age]:
			VaxFactory.age_pool[min_age][vax_center.id] = {
				"sessions": []
			}
		VaxFactory.age_pool[min_age][vax_center.id]["sessions"].append(session)

	@staticmethod
	def add_vax_pool(vax, vax_center, session):
		if vax not in VaxFactory.vax_pool:
			VaxFactory.vax_pool[vax] = {}
		if vax_center.id not in VaxFactory.vax_pool[vax]:
			VaxFactory.vax_pool[vax][vax_center.id] = {
				"sessions": []
			}
		VaxFactory.vax_pool[vax][vax_center.id]["sessions"].append(session)

	@staticmethod
	def get_center(id):
		return None if id not in VaxFactory.pool else VaxFactory.pool[id]

	@staticmethod
	def get_centers():
		return VaxFactory.pool.keys()

	@staticmethod
	def get_vaxes():
		return VaxFactory.vax_pool.keys()

	@staticmethod
	def get_age_pools():
		return VaxFactory.age_pool.keys()

	@staticmethod
	def add_center(id, name, addr, block, pincode,
				   lati, longi, session_id, session_date,
				   min_age_limit, vax, cap_avail,
				   cap_avail_dose1, cap_avail_dose2, slots):
		vax_center = VaxFactory.find_or_create(
			id, name, addr, block, pincode, lati, longi)
		vax_session = vax_center.add_session(
			session_id=session_id, session_date=session_date,
			min_age_limit=min_age_limit, vax=vax, cap_avail=cap_avail,
			cap_avail_dose1=cap_avail_dose1, cap_avail_dose2=cap_avail_dose2,
			slots=slots
		)
		VaxFactory.add_age_pool(min_age_limit, vax_center, vax_session)
		VaxFactory.add_vax_pool(vax, vax_center, vax_session)
		# VaxFactory.flush()

	@staticmethod
	def flush():
		VaxFactory.storage.store(VaxFactory.STORAGE_KEY, VaxFactory.export())

	@staticmethod
	def export():
		export_data = {}
		for each_center_id in VaxFactory.pool.keys():
			each_center = VaxFactory.pool[each_center_id]
			export_data[each_center_id] = each_center.export()
		return export_data

	@staticmethod
	def data_import(data, is_json=True):
		if not is_json:
			data = json.loads(data)
		for each_center_id in data.keys():
			vax_center = VaxCenter.data_import(data[each_center_id])
			VaxFactory.pool[int(each_center_id)] = vax_center
			for each_session in vax_center.session_data:
				VaxFactory.add_age_pool(
					each_session.min_age_limit, vax_center, each_session)
				VaxFactory.add_vax_pool(
					each_session.vax, vax_center, each_session)

	@staticmethod
	def boot():
		factory_data, ts = VaxFactory.storage.get(VaxFactory.STORAGE_KEY)
		if factory_data is not None:
			VaxFactory.data_import(factory_data)
