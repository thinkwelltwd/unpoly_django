import logging
from typing import List, Optional, TYPE_CHECKING

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import reverse
from django.template.response import TemplateResponse

from .unpoly import Unpoly

if TYPE_CHECKING:
    from .typehints import UnpolyHttpRequest

logger = logging.getLogger(__name__)


class UnpolyViewMixin:
    """
    This object allows the server to inspect the current request
    for Unpoly-related concerns such as "is this a page fragment update?".

    Available through the `up` method in all controllers, helpers and views.
    """
    if TYPE_CHECKING:
        request: 'UnpolyHttpRequest'

    action: str = ''
    _send_optimized_response: bool = False

    # Templates to use when returning an optimized response and Unpoly is returning a layer mode
    # https://v2.unpoly.com/layer-terminology
    unpoly_modal_template: str = settings.UNPOLY_MODAL_TEMPLATE
    unpoly_drawer_template: str = settings.UNPOLY_DRAWER_TEMPLATE
    unpoly_popup_template: str = settings.UNPOLY_POPUP_TEMPLATE
    unpoly_cover_template: str = settings.UNPOLY_COVER_TEMPLATE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._up: Optional[Unpoly] = None
        self._record_event_data = {}

    @property
    def up(self) -> Unpoly:
        if not self._up:
            self._up = Unpoly(meta=self.request.META, query_params=self.request.GET)
        return self._up

    def up_mode(self) -> str:
        """Override on subclasses to handle fail modes."""
        return self.up.mode()

    def get_unpoly_layer(self) -> str:
        """Override on subclasses to customize logic."""
        return self.up.layer()

    def get_unpoly_fail_layer(self):
        """Override on subclasses to customize logic."""
        return self.up.fail_layer()

    def get_template_names(self) -> List[str]:
        """Return Unpoly template name for the specified layer."""
        if self.up.is_unpoly():
            requested_name = self.up.template_name()
            if requested_name:
                return [requested_name]

            up_mode = self.up_mode()
            if up_mode == 'root':
                return super().get_template_names()

            template_name = getattr(self, f'unpoly_{up_mode}_template', '')
            if template_name:
                return [template_name]

        return super().get_template_names()

    def send_optimized_response(self) -> bool:
        """Should the server send an optimized HTML response?

        When this view is called, should the controller
        return optimized HTML response containing only the
        target(s) that Unpoly would insert / replace on page?

        Override on the subclassed view to extend logic
        determining when to send only HTML vs page redirect.
        """
        return self._send_optimized_response and self.up.is_unpoly()

    def record_event_data(self, **kwargs) -> dict:
        """Data that should be included in `record:crud` event

        Override on subclasses to customize.
        """
        if not self._record_event_data:
            try:
                record_id = self.object.id
            except AttributeError:
                self._record_event_data = kwargs
                return kwargs

            try:
                model_name = self.object.model_name()
            except AttributeError:
                model_name = self.object.__class__.__name__.lower()

            self._record_event_data = {
                'id': record_id,
                'action': self.action,
                'model_name': model_name,
            }

        self._record_event_data.update(kwargs)

        return self._record_event_data

    def optimized_response(self) -> TemplateResponse:
        """Return optimized HTML response containing the target(s) Unpoly requests.

        Return optimized HTML response containing the target(s)
        that Unpoly to insert / replace on page.

        Each view must implement this function.

        return TemplateResponse(
            request=self.request,
            template='main_body.html',
            context={
                'key1': 'value1',
                'key2': 'value2',
                'object': self.object,
            },
        )
        """
        raise NotImplementedError('Specify this method on each view')


class UnpolyFormViewMixin(UnpolyViewMixin):
    """
    Mixin class for views such as CreateView / UpdateView.
    Enables setting Unpoly target on forms and returning
    optimized responses.
    """
    _send_optimized_success_response: bool = False

    enable_messages_framework: bool = True
    success_message: str = ''

    def form_valid(self, form):
        """When form is saved, handle various situations that might occur.

            - If DatabaseError was raised, display message to user.
            - Return optimized response.
            - Return HttpResponseRedirect like normal `form_valid` behavior.
            - If multiple layer, launched from select field, Accept the layer,
              so the underlying select field on the Parent layer can be updated.
        """
        try:
            self.object = form.save()
        except DatabaseError as e:
            logger.exception(e)
            return self.handle_integrity_error_response()

        launched_from_select_field = self.request.GET.get('parent_select_field_id', '')
        if self.up.is_unpoly() and launched_from_select_field:
            return self.send_accept_layer(form, launched_from_select_field)

        msg = self.get_success_message(form.cleaned_data)
        if msg:
            messages.success(self.request, msg, extra_tags='safe')

        if self.send_optimized_success_response():
            response = self.optimized_success_response()
            self.up.emit(response, 'record:crud', self.record_event_data())
            return response

        return HttpResponseRedirect(self.get_success_url())

    def up_mode(self) -> str:
        if getattr(self, 'invalid_form_submission', False):
            return self.up.fail_mode()
        return super().up_mode()

    def form_invalid(self, form):
        """
        Set view attribute when form submission fails, to know
        how to choose the correct response template.
        """
        self.invalid_form_submission = True
        return super().form_invalid(form)

    def send_accept_layer(self, form, select_field_id) -> HttpResponse:
        """
        When Unpoly has opened multiple overlays and the form is saved successfully, then
        send the JSON details to enable updating the Select Field on the parent layer.
        """
        self.object = form.save()
        resp = HttpResponse(b'', status=200)
        data = {
            'id': self.object.id,
            'name': str(self.object),
            'parent_select_field_id': select_field_id,
        }
        self.up.accept_layer(resp, data)

        return resp

    def send_optimized_success_response(self) -> bool:
        """Should server send optimized HTML response after form is saved?

        When form is successfully saved, should the controller
        return optimized HTML response containing only the
        target(s) that Unpoly would insert / replace on page?

        Override on the subclassed view to extend logic
        determining when to send only HTML vs page redirect.

        When overriding, call this superclass method first
        to check for Unpoly status first.
        """
        return self._send_optimized_success_response and self.up.is_unpoly()

    def optimized_success_response(self) -> TemplateResponse:
        """When form is saved, return only HTML that matches Unpoly target(s).

        When form is successfully saved, return optimized HTML response containing
        the target(s) that Unpoly to insert / replace on page.

        Each view must implement this function.

        return TemplateResponse(
            request=self.request,
            template='single_row_table.html',
            context={
                'body_id': 'membership_body',
                'object': self.object,
            },
        )
        """
        raise NotImplementedError('Specify this method on each view')

    def get_success_message(self, cleaned_data: dict) -> str:
        """Add success message to response if desired.

        When returning Unpoly optimized response, the template must include the `messages`
        markup or the `messages` markup should have the `up_hungry` html attribute set.
        """
        if not self.enable_messages_framework:
            return ''

        try:
            return self.success_message % cleaned_data
        except Exception as e:
            logger.exception(e)
            return ''

    def perform_unpoly_validation(self, request):
        """
        Unpoly form validation calls form validation but should not save form.
        """
        try:
            instance = self.get_object()
        except (AttributeError, ImproperlyConfigured):
            instance = None

        form = self.get_form(
            data=request.POST,
            files=request.FILES,
            instance=instance,
            up_validate=True,
        )
        form.is_valid()
        return self.form_invalid(form)

    def handle_integrity_error_response(self):
        """Return helpful error to the user when an unhandled error occurs.

        Trying hard to return a slightly more intelligent error than Internal Server Error
        when database integrity errors are raised. Mostly we want to catch such errors and
        return messages in the form, but sometimes it's pretty hard to do.

        So at least return something more useful than a 500.
        """
        if self.up.is_unpoly():
            return TemplateResponse(self.request, settings.DEFAULT_UP_ERROR_TEMPLATE, status=409)

        return HttpResponseRedirect(reverse(settings.DEFAULT_ERROR_VIEW))

    def get_unpoly_target(self) -> str:
        """Sets Unpoly target in template context

        Forms can have html target set that Unpoly will replace when
        the server returns POST response when the form action is completed.

        Override on subclasses to customize logic for determining target.
        """
        return self.up.target()

    def get_unpoly_fail_target(self) -> str:
        """Sets Unpoly fail target in template context

        Forms can have html fail target set that Unpoly will replace when
        the server returns POST response when the form action is completed.

        Override on subclasses to customize logic for determining fail target.
        """
        return self.up.fail_target()

    def get_context_data(self, **kwargs) -> dict:
        """
        Add Unpoly target to context, so it can be used in templates.
        """
        return super().get_context_data(
            up_target=self.get_unpoly_target(),
            up_fail_target=self.get_unpoly_fail_target(),
            **kwargs,
        )

    def post(self, request, *args, **kwargs) -> HttpResponse:
        """Perform Unpoly form validation and return if Unpoly is in form validation mode.
        """
        if self.up.is_validating():
            return self.perform_unpoly_validation(request=request)

        return super().post(request, *args, **kwargs)


class UnpolyCrispyFormViewMixin(UnpolyFormViewMixin):
    """For views loading `django-crispy-forms`.

    Supports both Django Create / Update Generic views and Vanilla views.

    Initialize the crispy form with Unpoly data attributes
    that should be included on the form's HTML.
    """

    def __init__(self, *args, **kwargs):
        superclass = super()
        superclass.__init__(*args, **kwargs)
        self.is_vanilla_view = not hasattr(superclass, 'get_form_kwargs')

    def get_unpoly_target(self) -> str:
        try:
            return settings.MAIN_UP_TARGET_FORM_VIEW
        except AttributeError:
            return super().get_unpoly_target()

    def get_form_kwargs(self) -> dict:
        """Return the Unpoly form data attributes that should be included on the Crispy form tag.

        Override on subclassed views to refine if necessary.
        """
        if not self.up.is_unpoly():
            return {}

        up_kwargs = {
            'up_layer': self.get_unpoly_layer(),
            'up_fail_layer': self.get_unpoly_fail_layer(),
            'up_target': self.get_unpoly_target(),
            'up_fail_target': self.get_unpoly_fail_target(),
            'multi_layer': self.up.multi_layer(),
            'form_action': self.request.get_full_path(),
        }

        if not self.is_vanilla_view:
            kwargs = super().get_form_kwargs()
            up_kwargs.update(kwargs)

        return up_kwargs

    def get_form(self, *args, **kwargs):
        if self.is_vanilla_view:
            kwargs.update(self.get_form_kwargs())
        return super().get_form(*args, **kwargs)


__all__ = (
    'UnpolyViewMixin',
    'UnpolyFormViewMixin',
    'UnpolyCrispyFormViewMixin',
)
