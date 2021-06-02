from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

SECURE_COOKIE = not settings.DEBUG


def _unpoly_validate(self) -> bool:
    """Unpoly is validating but not saving a form"""
    return 'HTTP_X_UP_VALIDATE' in self.META


def _unpoly_target(self) -> str:
    """
    Comma-separated string of Target selector
    names of the element(s) Unpoly is swapping

    #content_panel,#breadcrumb_bar,.item_list
    """
    return self.META.get('HTTP_X_UP_TARGET', '')


def _is_unpoly(self) -> bool:
    """Request is triggered by Unpoly"""
    return (
        'HTTP_X_UP_VERSION' in self.META
        or 'HTTP_X_UP_MODE' in self.META
        or 'HTTP_X_UP_TARGET' in self.META
        or 'HTTP_X_UP_VALIDATE' in self.META
    )


class UnpolyMiddleware(MiddlewareMixin):

    def set_headers(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        For fullest browser support, set headers & cookies
        so Unpoly can detect method & location.
        """
        method = request.method
        response['X-Up-Location'] = request.get_full_path()
        response['X-Up-Method'] = method

        if method != 'GET':
            response.set_cookie('_up_method', method, secure=SECURE_COOKIE)
        else:
            response.delete_cookie('_up_method')

        return response

    def __call__(self, request: HttpRequest):
        request.unpoly_target = _unpoly_target.__get__(request)
        request.unpoly_validate = _unpoly_validate.__get__(request)
        request.is_unpoly = _is_unpoly.__get__(request)

        response = self.get_response(request)

        return self.set_headers(request, response)


__all__ = [
    'UnpolyMiddleware',
]
