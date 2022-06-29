from random import randint
import time
import zmq
from sensor import TemperatureSensor, HumiditySensor

context = zmq.Context(1)
worker = context.socket(zmq.REQ)

identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
worker.setsockopt_string(zmq.IDENTITY, identity)
worker.connect("tcp://localhost:5555")

temperature_sensor = TemperatureSensor()
humidity_sensor = HumiditySensor()


# TODO handshake

def main():
    while True:
        temperature, humidity = temperature_sensor.sample(), humidity_sensor.sample()
        worker.send_json({
            'temperature': temperature,
            'humidity': humidity
        })

        msg = worker.recv_multipart()
        if not msg:
            break

        print(msg)


y
time.sleep(10)  # Do some heavy work

if __name__ == '__main__':
    main()
