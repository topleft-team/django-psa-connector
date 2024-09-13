import requests
import logging

from django.conf import settings
from retrying import retry
from json import JSONDecodeError

from djpsa.api import exceptions as exc


RETRY_WAIT_EXPONENTIAL_MULTAPPLIER = 1000  # Initial number of milliseconds to
# wait before retrying a request.
RETRY_WAIT_EXPONENTIAL_MAX = 10000  # Maximum number of milliseconds to wait
# before retrying a request.

logger = logging.getLogger(__name__)


def retry_if_api_error(exception):
    """
    Return True if we should retry, False otherwise.

    Basically, don't retry on APIClientError, because those are the
    type of exceptions where retrying won't help (404s, 403s, etc.)
    """
    return type(exception) is exc.APIError


class APIClient:

    def __init__(self, conditions=None):
        self.conditions = conditions

        self.request_settings = settings.PSA_MODULE.get_request_settings()
        self.timeout = self.request_settings['timeout']

    def fetch_resource(self, endpoint_url, params=None, should_page=False,
                       retry_counter=None,
                       *args, **kwargs):
        """
        Issue a GET request to the specified REST endpoint.

        retry_counter is a dict in the form {'count': 0} that is passed in
        to verify the number of attempts that were made.
        """

        @retry(stop_max_attempt_number=self.request_settings['max_attempts'],
               wait_exponential_multiplier=RETRY_WAIT_EXPONENTIAL_MULTAPPLIER,
               wait_exponential_max=RETRY_WAIT_EXPONENTIAL_MAX,
               retry_on_exception=retry_if_api_error)
        def _fetch_resource(endpoint_url, params=None, should_page=False,
                            retry_counter=None, *args, **kwargs):
            if not retry_counter:
                retry_counter = {'count': 0}
            retry_counter['count'] += 1

            return self.request('GET',
                                endpoint_url,
                                params=params,
                                should_page=should_page,
                                *args,
                                **kwargs)

        if not retry_counter:
            retry_counter = {'count': 0}
        return _fetch_resource(endpoint_url, params=params,
                               should_page=should_page,
                               retry_counter=retry_counter,
                               *args, **kwargs)

    def request(self,
                method,
                endpoint_url=None,
                body=None,
                params=None,
                should_page=False,
                files=None,
                *args,
                **kwargs):
        """
        Issue the given type of request to the specified REST endpoint.
        """

        if not endpoint_url:
            endpoint_url = self._format_endpoint()

        params = self._format_params(params)

        logger.debug(
            'Making {} request to {}, body len {}, params {}'.format(
                method, endpoint_url, len(body) if body else 0, params
            )
        )

        try:
            response = self._request(method, endpoint_url, body, params=params)

        except requests.RequestException as e:
            logger.debug(
                'Request failed: {} {}: {}'.format(method, endpoint_url, e)
            )
            raise exc.APIError('{}'.format(e))

        if response.status_code == 204:  # No content
            return None
        elif 200 <= response.status_code < 300:
            try:
                return response.json()
            except JSONDecodeError as e:
                logger.error(
                    'Request failed during decoding JSON: GET {}: {}'
                    .format(endpoint_url, e)
                )
                raise exc.APIError('JSONDecodeError: {}'.format(e))
        elif response.status_code == 403:
            # TODO permissions exception from AT returns as 500, because
            #  it is terribly designed. Need to handle
            self._log_failed(response)
            raise exc.PermissionsException(
                self._prepare_error_response(response), response.status_code)
        elif response.status_code == 404:
            msg = 'Resource not found: {}'.format(response.url)
            logger.warning(msg)
            raise exc.NotFoundError(msg)
        elif 400 <= response.status_code < 499:
            self._log_failed(response)
            raise exc.APIClientError(
                self._prepare_error_response(response))
        elif response.status_code == 500:
            self._log_failed(response)
            raise exc.APIServerError(
                self._prepare_error_response(response))
        else:
            self._log_failed(response)
            raise exc.APIError(response)

    def _request(self, method, endpoint_url, body, params=None):
        raise NotImplementedError('Subclasses must implement this method.')

    def _format_endpoint(self):
        raise NotImplementedError('Subclasses must implement this method.')

    def _format_params(self, params=None):
        raise NotImplementedError('Subclasses must implement this method.')
