import signal
import sys
import asyncio

def handle_shutdown(*args):
    print("Shutting down...")
    loop = asyncio.get_event_loop()
    loop.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)