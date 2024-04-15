from django.core.cache import cache
from rest_framework.response import Response


class cache_response_handler(Response):
    """
    Makes an entry in Redis cache after returning the response hence asynchronous automatically.
    Conditions:
        1. If this request has to be cached or not
        2. If response status code is 200 (Safety Check for conndition 1)
        3. If request is of 'GET' type only (Safety Check for condition 1 and 2)

    """

    request = None
    cache_request = False

    def set_request(self, request=None):
        self.request = request
        return self.request

    def set_cache_request(self, cache=True):
        self.cache_request = cache
        return self.set_cache_request

    def close(self):
        super(cache_response_handler, self).close()
        if (
            self.status_code == 200
            and self.request.method == "GET"
            and self.cache_request
        ):
            cache.set(self.request.sha, self.data, timeout=60 * 15)
