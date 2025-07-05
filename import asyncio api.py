import asyncio
import logging
from typing import Callable, Any

# You can define this globally or pass it in
from thread_pool_manager import ThreadPoolManager

async def safe_api_call(
    func: Callable,
    *args,
    max_retries: int = 3,
    timeout: int = 5,
    priority: int = 1,
    executor_name: str = "api",
    **kwargs
) -> Any:
    """
    Executes a blocking API function in an async-safe way with retry, timeout, and priority handling.

    :param func: Blocking function to run
    :param args: Positional args for the function
    :param kwargs: Keyword args for the function
    :param max_retries: How many times to retry on failure
    :param timeout: Timeout per attempt in seconds
    :param priority: Lower is higher priority; adds delay for lower-priority jobs
    :param executor_name: Named thread pool (from thread_pool_manager)
    :return: Result of the function, or None if all retries fail
    """

    global api_flag
    loop = asyncio.get_running_loop()
    executor = ThreadPoolManager.get_executor(executor_name)

    # Optional priority delay
    if priority > 1:
        await asyncio.sleep((priority - 1) * 0.1)  # simple delay logic

    for attempt in range(1, max_retries + 1):
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(executor, lambda: func(*args, **kwargs)),
                timeout=timeout
            )

            if result in (None, [], {}):
                raise ValueError("Received empty or invalid result.")

            api_flag = True
            logging.info(f"[safe_api_call] {func.__name__} succeeded on attempt {attempt}")
            return result

        except Exception as e:
            api_flag = False
            logging.warning(f"[safe_api_call] {func.__name__} failed (attempt {attempt}/{max_retries}): {e}")
            await asyncio.sleep(0.2)

    logging.error(f"[safe_api_call] {func.__name__} failed after {max_retries} attempts.")
    return None
