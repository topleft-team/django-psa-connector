import requests
import logging

from django.conf import settings

from djpsa.api.client import APIClient
from djpsa.halo.utils import get_token, rm_token


logger = logging.getLogger(__name__)


class HaloAPICredentials:
    def __init__(self, resource_server, authorisation_server, client_id, client_secret):
        self.resource_server = resource_server
        if not self.resource_server.endswith('/'):
            self.resource_server += '/'
        self.authorisation_server = authorisation_server
        if not self.authorisation_server.endswith('/'):
            self.authorisation_server += '/'
        self.client_id = client_id
        self.client_secret = client_secret


class HaloAPIClient(APIClient):
    endpoint = None

    def __init__(self, conditions=None, credentials=None):
        super().__init__(conditions)
        if not credentials:
            credentials = HaloAPICredentials(
                settings.HALO_RESOURCE_SERVER,
                settings.HALO_AUTHORISATION_SERVER,
                settings.HALO_CLIENT_ID,
                settings.HALO_CLIENT_SECRET,
            )
        self.credentials = credentials

    def check_auth(self):
        return bool(get_token(self.credentials, use_cache=False))

    def get_page(self, page=None, params=None):
        params = params or {}
        if page:
            params['page_no'] = page
        return self.fetch_resource(params=params)

    def get(self, record_id):
        return self.request('GET', params={'search_id': record_id})

    def create(self, data):
        # TODO doesnt do anything yet
        return self.request('POST', body=data)

    def update(self, record_id, data):
        # TODO doesnt do anything yet
        return self.request('PUT', params={'id': record_id}, body=data)

    def _format_endpoint(self):
        return '{}{}'.format(self.credentials.resource_server, self.endpoint)

    def _format_params(self, params=None):
        params = params or {}
        request_params = {}

        for condition in self.conditions:
            request_params.update(condition)

        request_params.update(params)

        if 'page' in request_params:
            request_params['page_size'] = self.request_settings['batch_size']
            request_params['pageinate'] = True

        return request_params

    def _request(
            self, method, endpoint_url, headers=None, params=None, **kwargs):
        token = get_token(self.credentials)
        token_header = {'Authorization': f'Bearer {token}'}

        # If kwargs contains headers, update it with the token, if not,
        # create it
        if headers:
            headers.update(token_header)
        else:
            headers = token_header

        # Make the actual request
        response = requests.request(
            method,
            endpoint_url,
            headers=headers,
            params=params,
            **kwargs
        )

        # If the token is invalid, refresh it and retry
        if response.status_code == 401:
            rm_token()
            token = get_token(self.credentials)
            headers['Authorization'] = f'Bearer {token}'
            response = requests.request(
                method,
                endpoint_url,
                headers=headers,
                params=params,
                **kwargs
            )

        return response
