from prediction_history import PredictionHistory
from util.log import get_logger
from util.message_socket import MessageSocket
from util.periodic_task import PeriodicTask
from weather_sensors import WeatherSensors

logger = get_logger(__name__)


class PredictionController(PeriodicTask):
    _MESSAGE_TYPE = 'predict'

    def __init__(
            self,
            weather_sensors: WeatherSensors,
            message_socket: MessageSocket,
            prediction_history: PredictionHistory
    ):
        super().__init__(period_seconds=1)
        self._message_socket = message_socket
        self._weather_sensors = weather_sensors
        self._prediction_history = prediction_history

    async def run(self) -> None:
        sensor_data = self._weather_sensors.get_data()
        if not sensor_data:
            return
        await self._message_socket.send_json(type=PredictionController._MESSAGE_TYPE, data=sensor_data._asdict())

        response = await self._message_socket.receive()
        if not response:
            logger.warning(f'Received no response for sent message: {sensor_data}')
            return

        prediction = response.parts[0]
        self._prediction_history.add(prediction)
        print(f'Weather prediction: {prediction}\n\tlast predictions: {self._prediction_history}')
