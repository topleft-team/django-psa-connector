import os
import requests
import stat

from django.conf import settings

TOKEN_FILE = os.path.expanduser('~/.halo_token')


class APIClient(object):

    def __init__(self, url, params=None):
        self.url = get_resource_url(url)
        self.params = params

    def request(self, method='GET', params=None, json=None):
        """
        Make a GET request to the Halo API with a token, and if the token is
        invalid then retry once with a fresh token.
        :param method: the HTTP method to use
        :param params: the query parameters to use (dictionary)
        """
        if not params:
            params = self.params
        else:
            params.update(self.params)

        params['page_size'] = 50
        params['pageinate'] = True

        token_removed = False
        while True:
            token = get_token()
            response = requests.request(
                method,
                self.url,
                headers={
                    'Authorization': 'Bearer {}'.format(token),
                },
                params=params,
                json=json,
            )
            if response.status_code == 401 and not token_removed:
                # Token is invalid and we didn't already try to refresh it,
                # so remove it and try again with a new token.
                rm_token()
                token_removed = True
                continue
            break

        return response


def get_resource_url(resource):
    return '{}api/{}'.format(settings.HALO_API, resource)


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
