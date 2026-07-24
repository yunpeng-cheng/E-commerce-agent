"""
重试机制工具模块

提供统一的重试装饰器，用于处理外部服务（MySQL、Qdrant、ES、Embedding）的临时故障
"""

import asyncio
import random
from typing import Any, Callable, TypeVar

from tenacity import (
    AsyncRetrying,
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random_exponential,
)

# MySQL 相关异常
from sqlalchemy.exc import OperationalError, TimeoutError as SQLTimeoutError
from asyncmy.errors import OperationalError as AsyncmyOperationalError

# Qdrant/HTTP 相关异常
import httpx

# Elasticsearch 相关异常
from elasticsearch import exceptions as es_exceptions

# Embedding 相关异常
import aiohttp

from app.core.log import logger

# 定义类型变量
T = TypeVar("T")

# 重试配置
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MIN_WAIT = 1  # 秒
DEFAULT_MAX_WAIT = 10  # 秒


def retry_on_exception(
    exceptions: tuple[type[BaseException], ...],
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    min_wait: float = DEFAULT_MIN_WAIT,
    max_wait: float = DEFAULT_MAX_WAIT,
):
    """
    同步重试装饰器工厂

    Args:
        exceptions: 需要重试的异常类型元组
        max_attempts: 最大重试次数
        min_wait: 最小等待时间（秒）
        max_wait: 最大等待时间（秒）
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            retry=retry_if_exception_type(exceptions),
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            before_sleep=lambda retry_state: logger.warning(
                f"Retry {retry_state.attempt_number}/{max_attempts} "
                f"for {func.__name__} due to {retry_state.outcome.exception()}"
            ),
            reraise=True,
        )
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def async_retry_on_exception(
    exceptions: tuple[type[BaseException], ...],
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    min_wait: float = DEFAULT_MIN_WAIT,
    max_wait: float = DEFAULT_MAX_WAIT,
):
    """
    异步重试装饰器工厂

    Args:
        exceptions: 需要重试的异常类型元组
        max_attempts: 最大重试次数
        min_wait: 最小等待时间（秒）
        max_wait: 最大等待时间（秒）
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_state = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts for {func.__name__}: {e}"
                        )
                        raise
                    wait_time = min(
                        min_wait * (2 ** (attempt - 1)) + random.random() * 0.5,
                        max_wait,
                    )
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} "
                        f"due to {e}, waiting {wait_time:.2f}s"
                    )
                    await asyncio.sleep(wait_time)
            raise RetryError(retry_state)

        return wrapper

    return decorator


# 预定义的重试装饰器

# MySQL 重试装饰器
# 只重试临时的连接问题和超时，不重试业务逻辑错误（如数据校验失败）
async_mysql_retry = async_retry_on_exception(
    exceptions=(
        # SQLAlchemy 层面的异常
        OperationalError,
        SQLTimeoutError,
        # asyncmy 驱动层面的异常
        AsyncmyOperationalError,
        # 网络层异常
        ConnectionResetError,
        ConnectionRefusedError,
    ),
    max_attempts=3,
    min_wait=1,
    max_wait=5,
)

# Qdrant 重试装饰器
# 只重试网络层面的问题，不重试业务逻辑错误
async_qdrant_retry = async_retry_on_exception(
    exceptions=(
        # HTTP 层面的异常
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.WriteTimeout,
        # 网络层异常
        ConnectionResetError,
        ConnectionRefusedError,
        # Qdrant 客户端异常
        httpx.HTTPStatusError,  # 5xx 错误会被重试
    ),
    max_attempts=3,
    min_wait=1,
    max_wait=5,
)

# Elasticsearch 重试装饰器
# 只重试临时的连接问题和超时
async_es_retry = async_retry_on_exception(
    exceptions=(
        # ES 连接异常
        es_exceptions.ConnectionError,
        es_exceptions.ConnectionTimeout,
        # ES 服务器异常（5xx）
        es_exceptions.TransportError,
        # 网络层异常
        ConnectionResetError,
        ConnectionRefusedError,
    ),
    max_attempts=3,
    min_wait=1,
    max_wait=5,
)

# Embedding 重试装饰器
# Embedding 服务通常较耗时，重试间隔可以稍长
async_embedding_retry = async_retry_on_exception(
    exceptions=(
        # aiohttp 层面的异常
        aiohttp.ClientTimeout,
        aiohttp.ClientConnectionError,
        aiohttp.ClientError,
        # HTTP 层面的异常
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        # 网络层异常
        ConnectionResetError,
        ConnectionRefusedError,
    ),
    max_attempts=3,
    min_wait=2,
    max_wait=10,
)