"""
通用工具函数模块
"""

from typing import Any, Callable, Coroutine, TypeVar

from fastapi.concurrency import run_in_threadpool

# T is a type variable that can be any type.
T = TypeVar("T")


async def run_sync(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    在线程池中异步运行同步函数，避免阻塞事件循环。
    这是对 fastapi.concurrency.run_in_threadpool 的一个简单封装，
    以提供更简化的调用接口和清晰的命名。

    参数:
        func: 要在线程池中执行的同步函数。
        *args: 传递给该函数的位置参数。
        **kwargs: 传递给该函数的关键字参数。

    返回:
        函数 `func` 的返回值。
    """
    return await run_in_threadpool(func, *args, **kwargs)
