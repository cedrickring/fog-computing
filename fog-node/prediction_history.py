import collections
from typing import Deque


class PredictionHistory:

    def __init__(self, capacity: int = 5):
        self._deque: Deque[str] = collections.deque(maxlen=capacity)

    def add(self, prediction: str) -> None:
        self._deque.appendleft(prediction)

    def restore(self, history: list[str]):
        for entry in history:
            self._deque.append(entry)

    def __str__(self):
        return ", ".join(self._deque)
