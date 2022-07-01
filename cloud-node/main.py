import json

import zmq


def main():
    context = zmq.Context(1)

    socket = context.socket(zmq.ROUTER)  # ROUTER
    socket.bind("tcp://*:5555")

    i = 0
    while True:
        msg = socket.recv_multipart()
        print(msg)
        if not msg:
            break

        data = json.loads(msg[2])
        print(data)

        prediction = f'Sunny{i}'
        i += 1
        response = msg[:2] + [prediction.encode()]

        socket.send_multipart(response)


if __name__ == '__main__':
    main()
