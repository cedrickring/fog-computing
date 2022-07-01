import collections
import sys
import time
import zmq
from weather_sensors import WeatherSensors

context = zmq.Context(1)
socket = context.socket(zmq.REQ)

identity = sys.argv[1]
socket.setsockopt_string(zmq.IDENTITY, identity)
socket.connect("tcp://localhost:5555")

weather_sensors = WeatherSensors()
prediction_history = collections.deque(maxlen=5)


# TODO handshake

def main():
    while True:
        sensor_data = weather_sensors.next()
        print(f'Read sensor data: {sensor_data}')
        socket.send_json(sensor_data._asdict())

        msg = socket.recv_multipart()
        if not msg:
            break
        prediction = msg[0].decode()

        prediction_history.appendleft(prediction)
        print(f'Weather prediction: {prediction}, last predictions: {", ".join(prediction_history)}')

        time.sleep(1)


if __name__ == '__main__':
    main()
