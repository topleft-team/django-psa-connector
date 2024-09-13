import requests
import logging

from django.conf import settings

from djpsa.api.client import APIClient
from djpsa.halo.utils import get_token, rm_token


logger = logging.getLogger(__name__)


class HaloAPIClient(APIClient):
    endpoint = None

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

    def _request(self, method, endpoint_url, body, params=None):
        """
        Make request to the Halo API with a token, and if the token is
        invalid then retry once with a fresh token.
        :param method: the HTTP method to use
        :param params: the query parameters to use (dictionary)
        """

        token_removed = False
        while True:
            token = get_token()
            response = requests.request(
                method,
                endpoint_url,
                headers={
                    'Authorization': 'Bearer {}'.format(token),
                },
                params=params,
                json=body,
            )
            if response.status_code == 401 and not token_removed:
                # Token is invalid, and we didn't already try to refresh it,
                # so remove it and try again with a new token.
                rm_token()
                token_removed = True
                continue
            break

        return response

    def get_page(self, page=None):
        params = {}
        if page:
            params['page_no'] = page
        return self.request('GET', params=params)

    def get(self, record_id):
        # copilot generated - likely not useful other than placeholder
        return self.request('GET', params={'id': record_id})

    def create(self, data):
        # copilot generated - likely not useful other than placeholder
        return self.request('POST', body=data)

    def update(self, record_id, data):
        # copilot generated - likely not useful other than placeholder
        return self.request('PUT', params={'id': record_id}, body=data)


class TicketAPI(HaloAPIClient):
    endpoint = 'Tickets'


class ClientAPI(HaloAPIClient):
    endpoint = 'Client'


class StatusAPI(HaloAPIClient):
    endpoint = 'Status'


class PriorityAPI(HaloAPIClient):
    endpoint = 'Priority'


class AgentAPI(HaloAPIClient):
    endpoint = 'Agent'


class SLAAPI(HaloAPIClient):
    endpoint = 'SLA'


class SiteAPI(HaloAPIClient):
    endpoint = 'Site'


class UserAPI(HaloAPIClient):
    endpoint = 'Users'
