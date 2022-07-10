import json
from asyncio import Lock
from dataclasses import dataclass
from typing import Optional, Any, Callable, Awaitable

import zmq.asyncio

ReconnectCallback = Callable[[], Awaitable]

@dataclass
class ResponseMessage:
    sender: Optional[str]
    type: str
    parts: list[str]


@dataclass
class ReceivedMessage:
    sender: Optional[str]
    type: str
    parts: list[str]

    def read_json(self) -> Any:
        return json.loads(self.parts[0])

    def create_response(self, *args: str):
        return ResponseMessage(sender=self.sender, type=self.type, parts=list(args))


class MessageSocket:

    def __init__(self, host: str, port: int, socket_type: int, identity: str = None):
        self._host = host
        self._port = port
        self._context = zmq.asyncio.Context(io_threads=1)
        self._socket = self._context.socket(socket_type)

        self._lock: Optional[Lock] = None
        self._reconnect_callbacks: list[ReconnectCallback] = []
        if identity:
            self._socket.setsockopt_string(zmq.IDENTITY, identity)

    def bind(self) -> None:
        self._socket.bind(f'tcp://{self._host}:{self._port}')

    def connect(self) -> None:
        self._socket.connect(f'tcp://{self._host}:{self._port}')

    def shutdown(self):
        self._socket.close()

    def add_reconnect_callback(self, callback: ReconnectCallback) -> None:
        self._reconnect_callbacks.append(callback)

    async def notify_reconnect_callbacks(self) -> None:
        for callback in reversed(self._reconnect_callbacks):
            await callback()

    async def receive(self) -> Optional[ReceivedMessage]:
        message = await self._socket.recv_multipart()
        if not message:
            return None
        decoded_message = [part.decode() for part in message]

        sender: Optional[str] = None
        if len(message) > 2 and decoded_message[1] == '':  # identity is always the first entry followed by an empty string
            sender = decoded_message[0]
            decoded_message = decoded_message[2:]

        return ReceivedMessage(sender=sender, type=decoded_message[0], parts=decoded_message[1:])

    async def send_response(self, response: ResponseMessage) -> None:
        message = [response.type] + response.parts
        if response.sender:
            message = [response.sender, ''] + message  # identity must be the first entry followed by an empty string

        await self._socket.send_multipart([part.encode() for part in message])

    async def send_parts_and_receive(self, type: str, parts: list[str] = None, sender: str = None) -> Optional[ResponseMessage]:
        if parts is None:
            parts = []
        async with self._get_lock():
            await self.send_response(ResponseMessage(sender=sender, type=type, parts=parts))
            return await self.receive()

    async def send_string_and_receive(self, type: str, string: str, sender: str = None) -> Optional[ResponseMessage]:
        return await self.send_parts_and_receive(type=type, sender=sender, parts=[string])

    async def send_json_and_receive(self, type: str, data: Any, sender: str = None) -> Optional[ResponseMessage]:
        return await self.send_parts_and_receive(sender=sender, type=type, parts=[json.dumps(data)])

    def _get_lock(self) -> Lock:
        # lazily initialize lock, so we are in the correct event loop
        if not self._lock:
            self._lock = Lock()
        return self._lock
