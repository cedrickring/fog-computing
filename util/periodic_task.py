import asyncio
from abc import ABC, abstractmethod


class PeriodicTask(ABC):

    def __init__(self, period_seconds: int):
        self._period_seconds = period_seconds

    @abstractmethod
    async def run(self) -> None:
        ...

    async def start(self):
        while True:
            await self.run()
            try:
                await asyncio.sleep(self._period_seconds)
            except asyncio.CancelledError:
                break

