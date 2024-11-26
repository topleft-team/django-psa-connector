import redis
import logging
import requests

from djpsa.api.exceptions import APIError

from django.conf import settings

logger = logging.getLogger(__name__)
from django.core.cache import cache


CACHE_KEY = 'halo_token'
CACHE_TIMEOUT = 3600  # TODO: check this


def get_saved_token():
    token = cache.get(CACHE_KEY)
    if token:
        return token.decode('utf-8')


def save_token(token):
    logger.debug('Saving token to Redis')
    cache.set(CACHE_KEY, token, timeout=CACHE_TIMEOUT)


def rm_token():
    cache.delete(CACHE_KEY)


def get_token(credentials, use_cache=True):
    if use_cache:
        token = get_saved_token()
        if token:
            return token

    token = get_new_access_token(credentials)
    # Even if we don't use the cache, we should save the token for future requests
    # because requesting a new token might invalidate prior tokens.
    save_token(token)
    return token


def get_new_access_token(credentials):
    logger.debug('Getting new access token')
    token_url = '{}token'.format(credentials.authorisation_server)
    try:
        response = requests.post(
            token_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scope': 'all',
            }
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error('Failed to get token: %s', e)
        raise APIError(e)
    token = response.json()['access_token']
    return token
