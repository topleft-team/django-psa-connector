try:
    # Redis is optional
    import redis
except ImportError:
    redis = None

import logging
from contextlib import contextmanager
from django.conf import settings

redis_client = None
logger = logging.getLogger(__name__)


def get_redis_client():
    global redis_client

    if not redis_client:
        redis_client = redis.StrictRedis(
            host=settings.REDIS['host'],
            port=settings.REDIS['port'],
            password=settings.REDIS['password'],
        )

    return redis_client


class LockNotAcquiredError(Exception):
    """The lock could not be acquired."""
    pass


@contextmanager
def redis_lock(lock_name, timeout, blocking_timeout):
    """
    Get a distributed lock using Redis.
    https://redis.readthedocs.io/en/stable/connections.html#redis.asyncio.client.Redis.lock
    """
    lock = get_redis_client().lock(
        lock_name,
        timeout=timeout,
        blocking_timeout=blocking_timeout
    )
    acquired = lock.acquire(blocking=True)
    if not acquired:
        raise LockNotAcquiredError()
    try:
        yield acquired
    finally:
        try:
            lock.release()
        except redis.exceptions.LockNotOwnedError:
            pass
