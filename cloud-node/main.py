import json
import pickle
import zmq
from sklearn.preprocessing import MinMaxScaler

def main():
    context = zmq.Context(1)

    socket = context.socket(zmq.ROUTER)  # ROUTER
    socket.bind("tcp://*:5555")

    filepath = "../models/random_forest.sav"
    classifier, scaler, label_encoder = pickle.load(open(filepath, 'rb'))

    i = 0
    while True:
        msg = socket.recv_multipart()
        print(msg)
        if not msg:
            break

        data = json.loads(msg[2])
        print(data)
        norm_data = scaler.transform([list(data.values())])
        prediction = label_encoder.inverse_transform(classifier.predict(norm_data))
        i += 1
        response = msg[:2] + [prediction[0].encode()]

        socket.send_multipart(response)


if __name__ == '__main__':
    main()
