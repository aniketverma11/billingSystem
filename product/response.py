# Local imports
from .utils import generate_response_dict
from .exceptions import cache_response_handler


def cached_response(
    request, response_status="error", message=None, status=None, data=None, meta=None
):
    response_payload = generate_response_dict(
        status=response_status,
        message=message,
        data=data,
        meta=meta,
    )
    response = cache_response_handler(response_payload, status=status)
    response.set_request(request=request)
    return response
