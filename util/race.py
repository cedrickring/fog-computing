import asyncio
from typing import Iterable, Awaitable, TypeVar

T = TypeVar('T')


async def race(awaitables: Iterable[Awaitable[T]]) -> T:
    done, _ = await asyncio.wait(fs=awaitables, return_when=asyncio.FIRST_COMPLETED)
    return await done.pop()  # just return first finished task and we don't care about the remainders


async def timeout(timeout: int) -> TimeoutError:
    await asyncio.sleep(float(timeout) / 1000)
    return TimeoutError()
