import pandas as pd

from collections import namedtuple

WeatherData = namedtuple('WeatherData', ('temperature', 'humidity', 'wind_speed', 'wind_bearing', 'visibility', 'pressure'))


class WeatherSensors:

    def __init__(self):
        self._data = pd.read_csv('../data/sensor_data.csv')
        self._n_rows = self._data[self._data.columns[0]].count()
        self._index = 0

    def next(self) -> WeatherData:
        data = self._data.loc[self._index]
        self._index += 1
        if self._index == self._n_rows:
            self._index = 0
        return WeatherData(*tuple(data[1:]))
