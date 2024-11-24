import requests
import logging

from django.conf import settings

from djpsa.api.client import APIClient
from djpsa.halo.utils import get_token, rm_token


logger = logging.getLogger(__name__)


class HaloAPIClient(APIClient):
    endpoint = None

    def __init__(self, conditions=None, resource_server_url=None,
                 authorisation_server_url=None, client_id=None, client_secret=None
                 ):
        super().__init__(conditions)
        self.resource_server_url = resource_server_url or settings.HALO_RESOURCE_SERVER_URL
        self.authorisation_server_url = authorisation_server_url or settings.HALO_AUTHORISATION_SERVER_URL
        self.client_id = client_id or settings.HALO_CLIENT_ID
        self.client_secret = client_secret or settings.HALO_CLIENT_SECRET

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
        return '{}{}'.format(self.resource_server_url, self.endpoint)

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
        token = get_token(
            self.authorisation_server_url,
            self.client_id,
            self.client_secret
        )
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
            token = get_token(
                self.authorisation_server_url,
                self.client_id,
                self.client_secret
            )
            headers['Authorization'] = f'Bearer {token}'
            response = requests.request(
                method,
                endpoint_url,
                headers=headers,
                params=params,
                **kwargs
            )

        return response
