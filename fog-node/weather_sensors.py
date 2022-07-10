import collections
from collections import namedtuple
from typing import Deque, Optional

import pandas as pd

from util.periodic_task import PeriodicTask

WeatherData = namedtuple('WeatherData', ('temperature', 'humidity', 'wind_speed', 'wind_bearing', 'visibility', 'pressure'))


class WeatherSensors(PeriodicTask):

    def __init__(self):
        super().__init__(period_seconds=1)
        self._data = pd.read_csv('../data/sensor_data.csv')
        self._n_rows = self._data[self._data.columns[0]].count()
        self._sensor_history: Deque[WeatherData] = collections.deque(maxlen=20)
        self._index = 0

    async def run(self) -> None:
        self._sensor_history.append(self._next())

    def get_data(self) -> Optional[WeatherData]:
        try:
            return self._sensor_history.popleft()
        except IndexError:
            return None

    def get_all_data(self) -> list[WeatherData]:
        data: list[WeatherData] = []
        while len(self._sensor_history) > 0:
            data.append(self.get_data())
        return data

    def _next(self) -> WeatherData:
        data = self._data.loc[self._index]
        self._index += 1
        if self._index == self._n_rows:
            self._index = 0
        return WeatherData(*tuple(data[1:]))

    def __iter__(self):
        return self._sensor_history.__iter__()
