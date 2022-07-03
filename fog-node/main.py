import asyncio
import logging
import sys

import zmq

from prediction_controller import PredictionController
from prediction_history import PredictionHistory
from util.log import get_logger
from util.message_socket import MessageSocket
from weather_sensors import WeatherSensors

logger = get_logger(__name__)

message_socket = MessageSocket(socket_type=zmq.REQ, identity=sys.argv[1])
weather_sensors = WeatherSensors()
prediction_history = PredictionHistory()
prediction_controller = PredictionController(
    weather_sensors=weather_sensors,
    prediction_history=prediction_history,
    message_socket=message_socket
)


async def do_handshake():
    await message_socket.send_parts(type='hello')
    response = await message_socket.receive()
    if response.type != 'hello':
        raise Exception(f'Invalid handshake response, received {response}')

    cached_history = response.parts
    if len(cached_history) == 0:
        logger.warning('No history to restore.')
        return

    prediction_history.restore(history=cached_history)
    logger.info(f'Last weather predictions: {", ".join(cached_history)}')


async def main():
    message_socket.connect('localhost', 5555)
    await do_handshake()
    await asyncio.gather(
        weather_sensors.start(),
        prediction_controller.start()
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Shutting down...')
        message_socket.shutdown()
