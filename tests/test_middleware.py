from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from unpoly.middleware import UnpolyMiddleware


def get_response(req):
    """Callable to pass in to new-style Middleware init method"""
    response = HttpResponse({})
    return response


class UnpolyMiddlewareTestCase(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_no_headers_not_unpoly(self):
        middleware = UnpolyMiddleware(get_response)
        request = self.factory.get('/')
        response = middleware(request)
        self.assertFalse(request.is_unpoly())

    def test_target_header_is_unpoly(self):
        middleware = UnpolyMiddleware(get_response)
        request = self.factory.get('/', HTTP_X_UP_TARGET='.breadcrumb')
        response = middleware(request)
        self.assertTrue(request.is_unpoly())

    def test_validate_header_is_unpoly(self):
        middleware = UnpolyMiddleware(get_response)
        request = self.factory.get('/', HTTP_X_UP_VALIDATE='.breadcrumb')
        response = middleware(request)
        self.assertTrue(request.is_unpoly())

    def test_check_response_headers(self):
        """
        Response should set X-Up-Location and X-Up-Method headers
        """
        middleware = UnpolyMiddleware(get_response)
        request = self.factory.get('/')
        response = middleware(request)
        headers = {v[0]: v[1] for v in response._headers.values()}

        self.assertEqual(headers.get('X-Up-Location'), '/')
        self.assertEqual(headers.get('X-Up-Method'), 'GET')
