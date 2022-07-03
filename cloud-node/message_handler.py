import asyncio
import pickle
import timeit
import warnings

from prediction_histories import PredictionHistories
from util.log import get_logger
from util.message_socket import MessageSocket, ReceivedMessage

logger = get_logger(__name__)


class MessageHandler:

    def __init__(
            self,
            model_path: str,
            message_socket: MessageSocket,
            prediction_histories: PredictionHistories
    ):
        self._prediction_model = None
        self._model_path = model_path
        self._message_socket = message_socket
        self._prediction_histories = prediction_histories

    async def listen(self) -> None:
        self._load_model()
        while True:
            try:
                message = await self._message_socket.receive()
                if not message:
                    logger.warning('Received no message')
                    continue

                if message.type == 'predict':
                    await self._handle_predict(message)
                elif message.type == 'hello':
                    await self._handle_handshake(message)

            except asyncio.CancelledError:
                logger.info('Stopped listening for messages.')
                break

    def _load_model(self):
        start = timeit.default_timer()
        self._prediction_model = pickle.load(open(self._model_path, 'rb'))
        logger.info('Loaded prediction model in %.3fs', timeit.default_timer() - start)

    async def _handle_predict(self, message: ReceivedMessage):
        classifier, scaler, label_encoder = self._prediction_model
        sensor_data = message.read_json()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # silence sklearn warnings

            norm_data = scaler.transform([list(sensor_data.values())])
            prediction = label_encoder.inverse_transform(classifier.predict(norm_data))[0]
            print(f'({message.sender}) Predicted "{prediction}" for {sensor_data}')

            self._prediction_histories.add(message.sender, prediction)
            await self._message_socket.send_response(message.create_response(prediction))

    async def _handle_handshake(self, message: ReceivedMessage):
        history = self._prediction_histories.get(message.sender)
        await self._message_socket.send_response(message.create_response(*history))
