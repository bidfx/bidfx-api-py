__all__ = ["WebSocketTradingAPI"]


class WebSocketTradingAPI:
    def __init__(self, config_section):
        self._username = config_section["username"]
