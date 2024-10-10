import requests
import logging

from django.conf import settings

from djpsa.api.client import APIClient
from djpsa.halo.utils import get_token, rm_token


logger = logging.getLogger(__name__)


class HaloAPIClient(APIClient):
    endpoint = None

    def get_page(self, page=None):
        params = {}
        if page:
            params['page_no'] = page
        return self.request('GET', params=params)

    def get(self, record_id):
        return self.request('GET', params={'search_id': record_id})

    def create(self, data):
        # TODO doesnt do anything yet
        return self.request('POST', body=data)

    def update(self, record_id, data):
        # TODO doesnt do anything yet
        return self.request('PUT', params={'id': record_id}, body=data)

    def _format_endpoint(self):
        return '{}api/{}'.format(settings.HALO_API, self.endpoint)

    def _format_params(self, params=None):
        if not params:
            params = {}

        for condition in self.conditions:
            params.update(condition)

        if 'page' in params:
            params['page_size'] = self.request_settings['batch_size']
            params['pageinate'] = True

        return params

    def _request(
            self, method, endpoint_url, headers=None, params=None, **kwargs):
        token = get_token()
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
            token = get_token()
            headers['Authorization'] = f'Bearer {token}'
            response = requests.request(
                method,
                endpoint_url,
                headers=headers,
                params=params,
                **kwargs
            )

        return response
