import collections
import json
import sys
import time
import zmq

from util.message_encoding import encode_message, decode_message
from weather_sensors import WeatherSensors

context = zmq.Context(1)
socket = context.socket(zmq.REQ)

identity = sys.argv[1]
socket.setsockopt_string(zmq.IDENTITY, identity)
socket.connect("tcp://localhost:5555")

weather_sensors = WeatherSensors()
prediction_history = collections.deque(maxlen=5)
sensor_history = collections.deque(maxlen=5)

def do_handshake():
    socket.send_string('hello')
    response = decode_message(socket.recv_multipart())
    if response[0] != 'hello':
        raise Exception(f'Invalid handshake response, received {response}')

    cached_history = response[1:]
    if len(cached_history) == 0:
        print('No history to restore.')
        return

    for prediction in cached_history:
        prediction_history.append(prediction)
    print(f'Last weather predictions: {", ".join(cached_history)}')

def main():
    do_handshake()

    while True:
        sensor_data = weather_sensors.next()
        print(f'Read sensor data: {sensor_data}')
        socket.send_multipart(encode_message(['predict', json.dumps(sensor_data._asdict())]))

        msg = socket.recv_multipart()
        if not msg:
            break
        msg = decode_message(msg)
        prediction = msg[1]

        prediction_history.appendleft(prediction)
        print(f'Weather prediction: {prediction}, last predictions: {", ".join(prediction_history)}')

        time.sleep(1)


if __name__ == '__main__':
    main()
