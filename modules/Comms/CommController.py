from modules.Comms.Adapters.TelegramAdapter import TelegramAdapter

class CommController:
    ADAPTER_TELEGRAM = TelegramAdapter

    def __init__(self, adapter, config = {}) -> None:
        self.adapter = adapter(config = config)
    
    def send(self, msg):
        self.adapter.send(msg)

    def read_otp(self, timeout_s=30):
        return self.adapter.read_otp_channel(timeout_s)
