from modules.Comms.Adapters.TelegramAdapter import TelegramAdapter


class CommController:
	ADAPTER_TELEGRAM = TelegramAdapter

	def __init__(self, adapter, config={}) -> None:
		self.adapter = adapter(config=config)

	def send(self, msg):
		return self.adapter.send(msg)

	def read_otp(self, timeout_s=30):
		return self.adapter.read_otp_channel(timeout_s)

	def read_booking_slot(self, timeout_s=20):
		return self.adapter.read_booking_slot(timeout_s)
