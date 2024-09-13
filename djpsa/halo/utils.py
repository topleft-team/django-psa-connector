import os
import requests
import stat

from django.conf import settings


TOKEN_FILE = os.path.expanduser('~/.halo_token')


def get_saved_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return f.read()


def save_token(token):
    print('Saving token to {}'.format(TOKEN_FILE))
    with open(TOKEN_FILE, 'w') as f:
        os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)
        f.write(token)


def rm_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def get_new_access_token():
    print('Getting new access token')
    token_url = '{}auth/token'.format(settings.HALO_API)
    response = requests.post(
        token_url,
        data={
            'grant_type': 'client_credentials',
            'client_id': settings.HALO_CLIENT_ID,
            'client_secret': settings.HALO_CLIENT_SECRET,
            'scope': 'all',
        }
    )
    response.raise_for_status()
    token = response.json()['access_token']
    return token


def get_token():
    token = get_saved_token()
    if token:
        return token

    token = get_new_access_token()
    save_token(token)
    return token
