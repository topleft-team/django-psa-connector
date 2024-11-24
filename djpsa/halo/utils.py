import redis
import logging
import requests


from django.conf import settings

logger = logging.getLogger(__name__)


redis_client = redis.StrictRedis(
        host=settings.REDIS['host'],
        port=settings.REDIS['port'],
        password=settings.REDIS['password'],
    )


def get_saved_token():
    token = redis_client.get('halo_token')
    if token:
        return token.decode('utf-8')


def save_token(token):
    logger.debug('Saving token to Redis')
    redis_client.set('halo_token', token)


def rm_token():
    redis_client.delete('halo_token')


def get_token(authorisation_server_url, client_id, client_secret):
    token = get_saved_token()
    if token:
        return token

    token = get_new_access_token(authorisation_server_url, client_id, client_secret)
    save_token(token)
    return token


def get_new_access_token(authorisation_server_url, client_id, client_secret):
    logger.debug('Getting new access token')
    token_url = '{}token'.format(authorisation_server_url)
    response = requests.post(
        token_url,
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'all',
        }
    )
    response.raise_for_status()
    token = response.json()['access_token']
    return token
