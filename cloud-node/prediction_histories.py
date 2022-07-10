from collections import defaultdict, deque
from functools import partial
from typing import Deque


class PredictionHistories:

    def __init__(self, capacity: int = 5):
        self._histories: dict[str, Deque[str]] = defaultdict(partial(deque, maxlen=capacity))

    def add_all(self, identity: str, predictions: list[str]) -> None:
        for prediction in predictions:
            self._histories[identity].appendleft(prediction)

    def get(self, identity: str) -> list[str]:
        return list(self._histories[identity])
