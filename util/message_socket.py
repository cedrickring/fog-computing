import json
from dataclasses import dataclass
from typing import Optional, Any

import zmq.asyncio

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

    def __init__(self, socket_type: int, identity: str = None):
        self._context = zmq.asyncio.Context(io_threads=1)
        self._socket = self._context.socket(socket_type)
        if identity:
            self._socket.setsockopt_string(zmq.IDENTITY, identity)

    def bind(self, port: int, host='*') -> None:
        self._socket.bind(f'tcp://{host}:{port}')

    def connect(self, host: str, port: int) -> None:
        self._socket.connect(f'tcp://{host}:{port}')

    def shutdown(self):
        self._socket.close()

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

    async def send_parts(self, type: str, parts: list[str] = None, sender: str = None) -> None:
        if parts is None:
            parts = []
        await self.send_response(ResponseMessage(sender=sender, type=type, parts=parts))

    async def send_string(self, type: str, string: str, sender: str = None) -> None:
        await self.send_parts(type=type, sender=sender, parts=[string])

    async def send_json(self, type: str, data: Any, sender: str = None) -> None:
        await self.send_parts(sender=sender, type=type, parts=[json.dumps(data)])
