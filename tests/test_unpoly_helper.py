import json

from django.http import HttpResponse
from django.test import SimpleTestCase

from unpoly.unpoly import Unpoly
from .settings import MAIN_UP_TARGET, MAIN_UP_FAIL_TARGET


request_meta = {
    'HTTP_X_UP_VERSION': '2.0',
    'HTTP_X_UP_MODE': 'modal',
    'HTTP_X_UP_TARGET': MAIN_UP_TARGET,
    'HTTP_X_UP_FAIL_TARGET': MAIN_UP_FAIL_TARGET,
}
query_params = {
    'multi_layer': True,
}


class UnpolyHelperTest(SimpleTestCase):

    def test_unpoly_request_attrs(self):

        up = Unpoly(meta=request_meta)

        self.assertTrue(up.is_unpoly())
        self.assertFalse(up.is_validating())
        self.assertFalse(up.multi_layer())
        self.assertEqual(up.mode(), request_meta['HTTP_X_UP_MODE'])
        self.assertEqual(up.target(), request_meta['HTTP_X_UP_TARGET'])
        self.assertEqual(up.fail_target(), request_meta['HTTP_X_UP_FAIL_TARGET'])
        self.assertEqual(up.fail_target(), request_meta['HTTP_X_UP_FAIL_TARGET'])

        meta = request_meta.copy()
        meta['HTTP_X_UP_VALIDATE'] = '.company_id'
        up = Unpoly(meta=meta, query_params=query_params)

        self.assertTrue(up.multi_layer())
        self.assertTrue(up.is_validating())
        self.assertEqual(up.validate(), meta['HTTP_X_UP_VALIDATE'])

    def test_unpoly_response_accept_layer(self):

        up = Unpoly(meta=request_meta)
        response = HttpResponse(200)

        data = {'id': 1, 'name': 'boxcar'}
        up.accept_layer(response, data)
        self.assertTrue(response.has_header('X-Up-Accept-Layer'))
        self.assertEqual(response['X-Up-Accept-Layer'], json.dumps(data))

    def test_unpoly_response_emit(self):
        up = Unpoly(meta=request_meta)
        response = HttpResponse(200)

        data = {'id': 1, 'name': 'boxcar', 'action': 'unhitch'}
        up.emit(response, 'boxcar:unhitched', data)
        self.assertTrue(response.has_header('X-Up-Events'))
        self.assertEqual(response['X-Up-Events'], json.dumps([data]))

    def test_unpoly_response_emit_layer(self):
        up = Unpoly(meta=request_meta)

        # Test with no layer specified
        response = HttpResponse(200)
        data = {'id': 1, 'name': 'boxcar', 'action': 'unhitch'}
        up.layer_emit(response, 'boxcar:unhitched', data)
        self.assertTrue(response.has_header('X-Up-Events'))

        data['layer'] = 'current'
        self.assertEqual(response['X-Up-Events'], json.dumps([data]))

        # Test with specific layer specified
        response = HttpResponse(200)
        data = {'id': 1, 'name': 'boxcar', 'action': 'unhitch', 'layer': 'overlay'}
        up.layer_emit(response, 'boxcar:unhitched', data)
        self.assertTrue(response.has_header('X-Up-Events'))
        self.assertEqual(response['X-Up-Events'], json.dumps([data]))

        event_data = json.loads(response['X-Up-Events'])[0]
        self.assertIn('type', event_data)
        self.assertEqual(event_data['type'], 'boxcar:unhitched')
