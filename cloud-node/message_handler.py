import asyncio
import pickle
import timeit
import warnings

from prediction_histories import PredictionHistories
from util.log import get_logger
from util.message_socket import MessageSocket, ReceivedMessage, ResponseMessage

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
                elif message.type == 'ping':
                    await self._message_socket.send_response(ResponseMessage(sender=message.sender, type='pong', parts=[]))

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

            if isinstance(sensor_data, list):
                X = [list(data.values()) for data in sensor_data]
            else:
                X = [list(sensor_data.values())]

            norm_data = scaler.transform(X)
            predictions = label_encoder.inverse_transform(classifier.predict(norm_data))
            print(f'({message.sender}) Predicted "{", ".join(predictions)}" for {sensor_data}')

            self._prediction_histories.add_all(message.sender, predictions)
            await self._message_socket.send_response(message.create_response(*predictions))

    async def _handle_handshake(self, message: ReceivedMessage):
        history = self._prediction_histories.get(message.sender)
        await self._message_socket.send_response(message.create_response(*history))
