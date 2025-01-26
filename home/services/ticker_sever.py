import redis
import asyncio
import datetime

class TickerSever:

    def __new__(cls, server_name, group_name, loop_period = 1, *args, **kwargs):
        # Services
        cls.server_name = server_name
        cls.loop_period = loop_period

        # Message Queue
        cls.group_name = group_name
        cls.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
        # Server
        cls._running = False
        # Data
        cls.tickers = {}

        return super().__new__(cls)

    def _init_load(self):
        pass

    def _on_attach(self, symbol):
        return None

    def _on_detach(self, symbol, ticker):
        pass

    def attach(self, symbol):
        self.tickers[symbol] = self._on_attach(symbol)

    def detach(self, symbol):
        if symbol not in self.tickers:
            pass
        ticker = self.tickers[symbol]
        self._on_detach(symbol, ticker)
        del self.tickers[symbol]

    @classmethod
    def is_exist(cls):
        return cls._instance is not None

    async def start(self):
        if not self._running:
            self._running = True
            self._init_load()
            await asyncio.to_thread(self.running)

    async def stop(self):
        self._running = False

    def running(self):
        try:
            while self._running:
                print(f"{self.server_name} [{datetime.datetime.now().isoformat()}] looping")
                self.ib.sleep(self.loop_period)
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            print(f"{self.server_name} Services Stopping at {datetime.datetime.now().isoformat()}")
            self.ib.disconnect()
            with self._lock:
                type(self)._instance = None
            print(f"{self.server_name} Server shutdown at {datetime.datetime.now().isoformat()}")
