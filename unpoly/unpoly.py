from ast import literal_eval
import json
from django.conf import settings
from django.http import HttpResponse


class Unpoly:
    """Partial port of Unpoly rails gem from
    https://github.com/unpoly/unpoly/blob/master/lib/unpoly/rails/change.rb

    This object allows the server to inspect the current request
    for Unpoly-related concerns such as "is this a page fragment update?".

    Available through the `up` method in all controllers, helpers and views.
    """

    def __init__(self, meta: dict, query_params: dict = None) -> None:
        self.meta: dict = meta
        self.query_params: dict = query_params or {}

    def is_unpoly(self) -> bool:
        """Request is triggered by Unpoly
        """
        return 'HTTP_X_UP_VERSION' in self.meta or self.is_validating()

    def mode(self) -> str:
        """Unpoly allows you to stack multiple pages on top of each other.

        Each stack element is called a layer. The kind of layer
        (e.g. a modal dialog vs. a popup box) is called mode.
        The initial page is called the root layer.
        An overlay is any layer that is not the root layer.
        """
        return self.meta.get('HTTP_X_UP_MODE', settings.MAIN_UP_LAYER)

    def fail_mode(self) -> str:
        """Return layer mode requested by Unpoly when a request failure occurs.
        """
        return self.meta.get('HTTP_X_UP_FAIL_MODE', settings.MAIN_UP_FAIL_LAYER)

    def layer(self) -> str:
        """Return layer mode requested by Unpoly when a request succeeds.
        """
        return self.meta.get('HTTP_X_UP_LAYER', settings.MAIN_UP_LAYER)

    def fail_layer(self) -> str:
        """Return layer mode requested by Unpoly when a request fails.
        """
        return self.meta.get('HTTP_X_UP_FAIL_LAYER', settings.MAIN_UP_FAIL_LAYER)

    def multi_layer(self) -> bool:
        """Check query params for key indicating that this layer is multiple overlay.

        Needed to indicate when a layer was launched from a non-root layer, such as when
        a `select` field URL launched a form to create a new Record, required to finish
        the original form.

        Not part of Unpoly protocol.
        """
        return self.query_params.get('multi_layer')

    def accept_layer(self, response: HttpResponse, data: dict) -> HttpResponse:
        """Send X-Up-Accept-Layer and data to frontend to close the current layer.
        """
        response['X-Up-Accept-Layer'] = json.dumps(data, default=str)
        return response

    def fail_target(self) -> str:
        """Returns the CSS selector for a fragment that Unpoly will update in
        case of a failed response. Server errors or validation failures are
        all examples for a failed response (non-200 status code).

        The Unpoly frontend will expect an HTML response containing an element
        that matches this selector.

        Server-side code is free to optimize its response by only returning HTML
        that matches this selector.
        """
        return self.meta.get('HTTP_X_UP_FAIL_TARGET') or settings.MAIN_UP_FAIL_TARGET

    def target(self) -> str:
        """Returns the CSS selector for a fragment that Unpoly will update in
        case of a successful response (200 status code).

        The Unpoly frontend will expect an HTML response containing an element
        that matches this selector.

        Server-side code is free to optimize its successful response by only returning HTML
        that matches this selector.
        """
        return self.meta.get('HTTP_X_UP_TARGET') or settings.MAIN_UP_TARGET

    def is_validating(self) -> bool:
        """Returns whether the current form submission should be
        [validated](https://unpoly.com/input-up-validate) (and not be saved to the database).
        """
        return 'HTTP_X_UP_VALIDATE' in self.meta

    def validate(self) -> str:
        """If the current form submission is a [validation](https://unpoly.com/input-up-validate),
        this returns the name attribute of the form field that has triggered
        the validation.
        """
        return self.meta.get('HTTP_X_UP_VALIDATE', '')

    def title(self, response: HttpResponse, title: str) -> HttpResponse:
        """Forces Unpoly to use the given string as the document title.

        This is useful when you skip rendering the `<head>` in an Unpoly request.
        """
        response['X-Up-Title'] = title
        return response

    def emit(self, response: HttpResponse, event: str, data: dict = None) -> HttpResponse:
        """The server may set a response header to emit events with the requested fragment update.

        The header value is a JSON array. Each element in the array is a JSON object representing
         an event to be emitted on the document.

        The object property { "type" } defines the event's type. Other properties become properties
        of the emitted event object.

        :param response: Response object that will be returned from view
        :param event: Event name, such as user:created
        :param data: Data dict to ship to the front end as the event value

        Eventual header value will look like so:
            X-Up-Events: [{"type": "user:created", "id": 5012 }, { "type": "signup:completed"}]
        """
        try:
            events = literal_eval(response['X-Up-Events'])
        except KeyError:
            events = []

        data = data or {}
        data['type'] = event
        events.append(data)
        response['X-Up-Events'] = json.dumps(events, default=str)

        return response

    def layer_emit(self, response: HttpResponse, event: str, data: dict = None) -> HttpResponse:
        """The server may also choose to emit the event on the layer being updated.

         To do so, add a property { "layer": "current" } to the JSON object of an event:

        Eventual header value will look like so:
            X-Up-Events: [{"type": "user:created", "name:" "foobar", "layer": "current"}]
        """
        data = data or {}
        if 'layer' not in data:
            data['layer'] = 'current'
        return self.emit(response, event, data)

    def template_name(self) -> str:
        """Return the template name that Unpoly or any other XHR request specified.

        Not part of the official Unpoly Server Protocol, but can be useful to as a
        way to signal to the server the exact template that should be rendered and
        returned as the response.
        """
        return self.meta.get('HTTP_X_TEMPLATE_NAME', '')

    def template_type(self) -> str:
        """Return the template type that Unpoly or any other XHR request specified.

        Not part of the official Unpoly Server Protocol, but can be useful to as a
        way to signal to the server that a given template type is desired.
        """
        return self.meta.get('HTTP_X_TEMPLATE_TYPE', '')
