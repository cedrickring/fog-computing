import random
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')


class DataSource(ABC, Generic[T]):

    @abstractmethod
    def next(self) -> T:
        pass


class ListDataSource(Generic[T], DataSource[T]):
    def __init__(self, items: list[T]):
        self._items = items
        self._length = len(items)

    def next(self) -> T:
        return self._items[random.randrange(self._length)]


class Sensor(Generic[T], ABC):

    def __init__(self, data_source: DataSource[T]):
        self._data_source = data_source

    def sample(self) -> T:
        return self._data_source.next()


class TemperatureSensor(Sensor[int]):
    def __init__(self):
        super().__init__(ListDataSource([21, 19, 24, 10]))


class HumiditySensor(Sensor[float]):
    def __init__(self):
        super().__init__(ListDataSource([0.43, 0.41, 0.45, 0.51, 0.59, 0.66, 0.72]))

