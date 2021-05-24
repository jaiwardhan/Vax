import hashlib
import getopt
import sys


class Utils:
	class Encoding:
		@staticmethod
		def sha256(sample):
			return hashlib.sha256(str(sample).encode()).hexdigest()

	class UserAgents:
		@staticmethod
		def mac():
			return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

		@staticmethod
		def android():
			return 'Mozilla/5.0 (Linux; Android 11; IN2021) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36'

	@staticmethod
	def get_opts(argv):
		try:
			opts, args = getopt.getopt(
				argv, "m:f:e:", ["mode=", "frequency=", "env="])
		except getopt.GetoptError:
			print('Illegal option usage. Abort.')
			sys.exit(2)

		data = {}
		for opt, arg in opts:
			data[opt] = arg
		return data
