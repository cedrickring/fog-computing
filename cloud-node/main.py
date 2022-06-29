import json

import zmq


def main():
    context = zmq.Context(1)

    socket = context.socket(zmq.ROUTER)  # ROUTER
    socket.bind("tcp://*:5555")

    while True:
        msg = socket.recv_multipart()
        print(msg)
        if not msg:
            break

        data = json.loads(msg[2])

        response = msg[:2] + [b'warm' if data['temperature'] >= 20 else b'cold',
                              b'humid' if data['humidity'] >= .5 else b'arid']

        socket.send_multipart(response)


if __name__ == '__main__':
    main()
