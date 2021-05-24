import json
import time
from modules.Config import APILoader, Network
from modules.Device import UserAgents
from modules.Storage import Storage
from modules.Logger import Logger
from modules.Utils import Utils


class Session():

	STORAGE_KEY_TOKEN = "TOKEN"
	STORAGE_KEY_OTP_GEN_TXNID = "OTP_TXNID"

	def __init__(self, phone_number, secret, force=False, capcom=None):
		self.secret = secret
		self.phone_number = str(phone_number)
		self.storage = Storage()
		self.capcom = capcom
		self.reset(force)

	def otp_prompt(self):
		otp = ""
		if self.capcom is None:
			otp = input("Enter OTP:")
		else:
			otp = self.capcom.read_otp()
		return otp

	def reset(self, force=False):
		last_txn_id, last_txn_ts = self.storage.get(
			Session.STORAGE_KEY_OTP_GEN_TXNID)
		last_token, last_token_ts = self.storage.get(Session.STORAGE_KEY_TOKEN)

		if force:
			if last_txn_id or last_token:
				self.storage.delete(Session.STORAGE_KEY_OTP_GEN_TXNID)
				self.storage.delete(Session.STORAGE_KEY_TOKEN)
				return self.reset()

		# If token is too old, we will need to reset all
		# @TODO reduce 15hr to 15min
		self.token = None \
			if last_token_ts is None or last_token_ts + (15*60*60) <= int(time.time()) \
			else last_token
		self.token_ts = None if self.token is None else last_token_ts
		self.req_refresh = self.token is None
		self.txnid_otp_generate = None if self.token is None else last_txn_id
		self.txnid_otp_generate_ts = None if self.txnid_otp_generate is None else last_txn_ts

	def needs_refresh(self):
		return self.req_refresh == True

	def otp_generate(self):
		# Reset and start
		# self.reset()
		headers = Network.headers_json()
		headers['User-Agent'] = UserAgents.android()
		payload = {
			"mobile": self.phone_number
		}
		api_url, method = APILoader.otp_generate()
		resp = method(
			api_url,
			headers=headers,
			data=json.dumps(payload)
		)
		if resp is not None:
			if int(resp.status_code) < 300:
				data = resp.json()
				if "txnId" in data:
					txn_id = data["txnId"]
					Logger.log("Txn id", txn_id)
					self.storage.store(
						Session.STORAGE_KEY_OTP_GEN_TXNID, txn_id)
					self.txnid_otp_generate, self.txnid_otp_generate_ts = self.storage.get(
						Session.STORAGE_KEY_OTP_GEN_TXNID)
					return True
				else:
					Logger.log("txnid not in response data:", data)
			else:
				Logger.log(resp.status_code, "::", resp.content.decode())
				if int(resp.status_code) == 400 and resp.content.decode() == "OTP Already Sent":
					return True
		return False

	def otp_validate(self, with_otp):
		headers = Network.headers_json()
		headers['User-Agent'] = UserAgents.android()
		self.txnid_otp_generate, self.txnid_otp_generate_ts = self.storage.get(
			Session.STORAGE_KEY_OTP_GEN_TXNID)
		Logger.log("Txn id is: ", self.txnid_otp_generate)
		payload = {
			"otp": Utils.Encoding.sha256(with_otp),
			"txnId": self.txnid_otp_generate
		}
		api_url, method = APILoader.otp_validate()
		resp = method(
			api_url,
			headers=headers,
			data=json.dumps(payload)
		)
		if resp is not None:
			if int(resp.status_code) < 300:
				data = resp.json()
				if "token" in data:
					self.token = data["token"]
					self.storage.store(Session.STORAGE_KEY_TOKEN, self.token)
					return True
				else:
					Logger.log("token not in data:", data)
			else:
				Logger.log(resp.status_code, "::", resp.content.decode())
				error_response = json.loads(resp.content.decode())
				if "errorCode" in error_response:
					# Beneficiary not registered
					if "USRAUT0024" == error_response["errorCode"]:
						Logger.log(" => Beneficiary not registered")
		return False

	def login(self):
		logged_in = not self.needs_refresh()
		if self.needs_refresh():
			Logger.log(".: Starting new session :.")
			if self.otp_generate():
				logged_in = self.otp_validate(self.otp_prompt())
		else:
			Logger.log(":: Session is already valid ::")
		return logged_in

	def export(self):
		return [self.token, self.phone_number, self.txnid_otp_generate]
