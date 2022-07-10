import asyncio
import logging
from typing import TypeVar

from util.message_socket import MessageSocket, ReceivedMessage
from util.periodic_task import PeriodicTask
from util.race import race, timeout

T = TypeVar('T')

_MAX_MISSES = 3
_PING_TIMEOUT_MS = 500
_TIMEOUT_ERROR = TimeoutError('Timeout')

logger = logging.getLogger(__name__)


class HeartbeatController(PeriodicTask):

    def __init__(self, message_socket: MessageSocket):
        super().__init__(1)
        self._message_socket = message_socket
        self._misses = 0

    async def run(self) -> None:
        try:
            await self._do_heartbeat()
            self._misses = 0
        except TimeoutError:
            self._misses += 1
            logger.warning(f'Missed heartbeat ({self._misses}/{_MAX_MISSES})')

        if self._misses == _MAX_MISSES:
            logger.warning(f'Missed {_MAX_MISSES} heartbeats. Waiting for reconnect...')
            while True:
                try:
                    await self._do_heartbeat()
                    logger.info('Reconnected')
                    self._misses = 0
                    await self._message_socket.notify_reconnect_callbacks()
                    break
                except TimeoutError:
                    logger.info(f'Trying again in 1s...')
                    await asyncio.sleep(1)

    async def _do_heartbeat(self) -> ReceivedMessage:
        result = await race([timeout(_PING_TIMEOUT_MS), self._message_socket.send_parts_and_receive(type='ping')])
        if isinstance(result, ReceivedMessage):
            if result.type != 'pong':
                raise Exception(f'Received message of type "pong", received: {result.type}')
            return result
        raise result
