import asyncio
import sys

import zmq

from heartbeat_controller import HeartbeatController
from prediction_controller import PredictionController
from prediction_history import PredictionHistory
from util.log import get_logger
from util.message_socket import MessageSocket
from util.race import race, timeout
from weather_sensors import WeatherSensors

logger = get_logger(__name__)

if len(sys.argv) < 2:
    print("Usage: python main.py <identity> [host]")
    sys.exit(1)
elif len(sys.argv) < 3:
    identity = sys.argv[1]
    hostname = "localhost"
else:
    identity = sys.argv[1]
    hostname = sys.argv[2]

message_socket = MessageSocket(host=hostname, port=40000, socket_type=zmq.REQ, identity=identity)
weather_sensors = WeatherSensors()
prediction_history = PredictionHistory()
prediction_controller = PredictionController(
    weather_sensors=weather_sensors,
    prediction_history=prediction_history,
    message_socket=message_socket
)
heartbeat_controller = HeartbeatController(
    message_socket=message_socket
)


async def do_handshake():
    response = await race([timeout(500), message_socket.send_parts_and_receive(type='hello')])
    if isinstance(response, TimeoutError):
        raise Exception('Failed to establish connection')

    if response.type != 'hello':
        raise Exception(f'Invalid handshake response, received {response}')

    cached_history = response.parts
    if len(cached_history) == 0:
        logger.warning('No history to restore.')
        return

    prediction_history.restore(history=cached_history)
    logger.info(f'Last weather predictions: {", ".join(cached_history)}')


async def main():
    message_socket.connect()
    await do_handshake()
    await asyncio.gather(
        heartbeat_controller.start(),
        weather_sensors.start(),
        prediction_controller.start(),
    )


if __name__ == '__main__':
    exit_code = 0
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Shutting down...')
    except Exception as ex:
        logger.exception('Application threw unrecoverable error:')
        exit_code = 1
    finally:
        message_socket.shutdown()
    sys.exit(exit_code)