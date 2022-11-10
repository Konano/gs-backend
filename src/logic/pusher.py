import httpx
from collections import deque
from typing import Dict, Deque
import time

from .. import utils
from .. import secret

class Pusher:
    THROTTLE_TIME_S = 30*60
    THROTTLE_N = 6

    def __init__(self) -> None:
        self.chan_history: Dict[str, Deque[float]] = {}

    async def push_message(self, msg: str, chan: str) -> None:
        print('push message', chan, msg)
        if not secret.FEISHU_WEBHOOK_ADDR:
            return

        hist = self.chan_history.get(chan, None)
        if hist is None:
            hist = deque()
            self.chan_history[chan] = hist

        if len(hist) >= self.THROTTLE_N:
            if time.time() - hist[0] < self.THROTTLE_TIME_S:
                print(f'push throttled, time bound = {time.time()-hist[0]}')
                return
            hist.popleft()
        hist.append(time.time())

        async with httpx.AsyncClient(http2=True) as client:
            try:
                await client.post(secret.FEISHU_WEBHOOK_ADDR, json={
                    'msg_type': 'text',
                    'content': {
                        'text': str(msg),
                    },
                })
            except Exception as e:
                print('PUSH MESSAGE FAILED', utils.get_traceback(e))
                pass