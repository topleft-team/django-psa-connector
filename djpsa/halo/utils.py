import redis
import logging
import requests
from contextlib import contextmanager

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# One hour in seconds, minus 60 seconds for buffer
CACHE_EXPIRE_TIME = 3540
REQUEST_TIMEOUT = 30
LOCK_TIMEOUT = REQUEST_TIMEOUT + 1
BLOCK_TIMEOUT = 60
TOKEN_NAME = 'halo_token'

redis_client = None


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
    """Custom exception raised when the lock is not acquired."""
    pass


@contextmanager
def redis_lock(lock_name):
    if getattr(settings, 'TOKEN_LOCK_DISABLED', False):
        # If the lock is not needed by a user, don't bother acquiring it
        yield True
        return

    lock = get_redis_client().lock(
        lock_name, timeout=LOCK_TIMEOUT, blocking_timeout=BLOCK_TIMEOUT)
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


def get_saved_token():
    return cache.get(TOKEN_NAME)


def save_token(token):
    logger.debug('Saving token to Redis')

    # Save the token to the cache
    cache.set(TOKEN_NAME, token, CACHE_EXPIRE_TIME)


def get_token():
    token = get_saved_token()
    if token:
        return token

    try:
        with redis_lock('halo_token_lock'):
            # Check if a valid token is already available, may
            # have been fetched by another worker thread while we
            # were waiting
            token = get_saved_token()
            if token:
                return token

            # No valid token, get a new one
            token = get_new_access_token()
            save_token(token)
            return token
    except LockNotAcquiredError as e:
        logger.error(f"Could not acquire lock: {e}")


def get_new_access_token():
    logger.debug('Getting new access token')
    token_url = '{}auth/token'.format(settings.HALO_API)
    response = requests.post(
        token_url,
        data={
            'grant_type': 'client_credentials',
            'client_id': settings.HALO_CLIENT_ID,
            'client_secret': settings.HALO_CLIENT_SECRET,
            'scope': 'all',
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    token = response.json()['access_token']

    return token
