import json
import warnings
from collections import defaultdict, deque
from functools import partial
from typing import Deque

import pickle
import zmq

from util.message_encoding import encode_message

filepath = "../models/random_forest.sav"
classifier, scaler, label_encoder = pickle.load(open(filepath, 'rb'))

prediction_histories: dict[str, Deque[str]] = defaultdict(partial(deque, maxlen=5))


def main():
    context = zmq.Context(1)

    socket = context.socket(zmq.ROUTER)  # ROUTER
    socket.bind("tcp://*:5555")

    print('listening')

    while True:
        msg = socket.recv_multipart()
        if not msg:
            break

        msg = [part.decode() for part in msg]
        sender, msg_type, parts = msg[0], msg[2], msg[3:]
        response: list[str] = []
        if msg_type == "hello":
            response = handle_handshake(sender, parts)
        elif msg_type == 'predict':
            response = handle_predict(sender, parts)

        multipart_res = encode_message([sender, '', msg_type] + response)
        socket.send_multipart(multipart_res)


def handle_handshake(sender: str, message: list[str]) -> list[str]:
    history = prediction_histories[sender]
    return list(history)


def handle_predict(sender: str, message: list[str]) -> list[str]:
    sensor_data = json.loads(message[0])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # silence sklearn warnings

        norm_data = scaler.transform([list(sensor_data.values())])
        prediction = label_encoder.inverse_transform(classifier.predict(norm_data))[0]
        print(f'({sender}) Predicted "{prediction}" for {sensor_data}')
        prediction_histories[sender].appendleft(prediction)
        return [prediction]


if __name__ == '__main__':
    main()
