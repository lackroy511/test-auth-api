import asyncio
import logging
from functools import wraps
from typing import Any, Callable

log = logging.getLogger(__name__)


class Backoff:
    def __init__(
        self,
        exceptions: tuple,
        start_delay: float = 0.1,
        factor: int = 2,
        max_delay: int = 1,
    ) -> None:
        self.exceptions = exceptions

        self.start_delay = start_delay
        self.factor = factor
        self.max_delay = max_delay

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            delay = self.start_delay

            while True:
                try:
                    result = await func(*args, **kwargs)
                    delay = self.start_delay
                    return result
                except self.exceptions as e:
                    await asyncio.sleep(delay)
                    if delay < self.max_delay:
                        delay *= self.factor

                    if delay >= self.max_delay:
                        log.exception("Error after Backoff retries:")
                        raise e

        return wrapper
