import time
import redis
import logging
import requests
from contextlib import contextmanager

from django.conf import settings

logger = logging.getLogger(__name__)

ONE_HOUR = 3600
REQUEST_TIMEOUT = 30
LOCK_TIMEOUT = REQUEST_TIMEOUT + 1
BLOCK_TIMEOUT = 60

redis_client = None


def get_redis_client():
    global redis_client
    if redis_client:
        return redis_client

    else:
        redis_client = redis.StrictRedis(
            host=settings.REDIS['host'],
            port=settings.REDIS['port'],
            password=settings.REDIS['password'],
        )


class LockNotAcquiredError(Exception):
    """Custom exception raised when the lock is not acquired."""
    pass


@contextmanager
def redis_lock(lock_name):
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
    token_data = get_redis_client().hgetall('halo_token')
    if not token_data:
        return None

    token = token_data.get(b'token')
    expiry = token_data.get(b'expiry')

    # Check if the token has expired
    if expiry and float(expiry) > time.time():
        return token.decode('utf-8')

    # Token expired, remove it
    rm_token()
    return None


def save_token(token):
    logger.debug('Saving token to Redis')
    # Subtract some time for buffer, say 60 seconds
    expiry_time = time.time() + ONE_HOUR - 60
    get_redis_client().hset('halo_token',
                            mapping={'token': token, 'expiry': expiry_time})


def rm_token():
    get_redis_client().delete('halo_token')


def get_token():
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
        print(f"Could not acquire lock: {e}")


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
