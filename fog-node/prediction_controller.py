from typing import Union

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
        message_socket.add_reconnect_callback(self._on_reconnect)
        self._weather_sensors = weather_sensors
        self._prediction_history = prediction_history

    async def _on_reconnect(self):
        sensor_data = self._weather_sensors.get_all_data()
        predictions = await self._request_predictions([data._asdict() for data in sensor_data])
        for prediction in predictions:
            self._prediction_history.add(prediction)
        print(f'Received predictions {", ".join(predictions)} for all saved weather data.')

    async def run(self) -> None:
        sensor_data = self._weather_sensors.get_data()
        if not sensor_data:
            return
        prediction = (await self._request_predictions(sensor_data._asdict()))[0]
        self._prediction_history.add(prediction)
        print(f'Weather prediction: {prediction}\n\tlast predictions: {self._prediction_history}')

    async def _request_predictions(self, sensor_data: Union[dict, list[dict]]) -> list[str]:
        response = await self._message_socket.send_json_and_receive(type=PredictionController._MESSAGE_TYPE, data=sensor_data)
        if not response:
            logger.warning(f'Received no response for sent message: {sensor_data}')
            return []

        return response.parts
