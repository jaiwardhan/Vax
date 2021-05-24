import json
from modules.Logger import Logger
import os
import time
from modules.Env import Env

class Storage:
	BASE_PATH = "storage.json"

	def __init__(self) -> None:
		self.data_store = {}
		if not os.path.exists(Storage.BASE_PATH):
			with open(Storage.BASE_PATH, "a+") as s:
				s.write('{}')
		elif not os.path.isfile(Storage.BASE_PATH):
			raise ValueError("Unable to store. A remnant with same name is present.")
		self.__resync()
	
	def __sync(self):
		with open(Storage.BASE_PATH, "w") as s:
			s.write(json.dumps(self.data_store))
	
	def __resync(self):
		contents = '{}'
		try:
			with open(Storage.BASE_PATH) as f:
				contents = f.read()
		except Exception as e:
			Logger.log(str(e))
		finally:
			self.data_store = json.loads(contents)
	
	def refresh(self):
		self.__resync()

	def store(self, key, value):
		if Env.mode() not in self.data_store:
			self.data_store[Env.mode()] = {}
		self.data_store[Env.mode()][str(key)] = {
			"value": value,
			"ts": int(time.time())
		}
		self.__sync()
	
	def delete(self, key):
		if Env.mode() not in self.data_store:
			self.data_store[Env.mode()] = {}
		v, _ = self.get(key)
		if v:
			del self.data_store[Env.mode()][str(key)]
		self.__sync()
	
	def get(self, key, default = None):
		partition = {} if Env.mode() not in self.data_store else self.data_store[Env.mode()]
		if str(key) not in partition:
			return default, 0
		else:
			return partition[str(key)]["value"], partition[str(key)]["ts"]
