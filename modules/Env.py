import os


class Env:
	KEY = "VAX_MODE"

	@staticmethod
	def set_mode(live=False):
		os.environ[Env.KEY] = "live" if live == True else "demo"

	@staticmethod
	def mode():
		env_val = os.getenv(Env.KEY)
		return "demo" if env_val is None or (env_val != "live" and env_val != "demo")\
			else env_val

	@staticmethod
	def set(key, value):
		if str(key) == "VAX_MODE":
			Env.set_mode(str(key), False if str(value) == 'False' else True)
			return
		os.environ[str(key)] = str(value)

	@staticmethod
	def get(key, default=None):
		return default if not os.getenv(str(key)) else os.getenv(str(key))
