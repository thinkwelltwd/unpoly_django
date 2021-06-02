from vanilla import CreateView as VanillaCreateView

from django.conf import settings
from django.db import models
from django import forms
from django.test import RequestFactory, SimpleTestCase
from django.views.generic import TemplateView, CreateView as DjangoCreateView

from unpoly.forms import UnpolyCrispyFormMixin
from unpoly.unpoly import Unpoly
from unpoly.views import UnpolyFormViewMixin, UnpolyCrispyFormViewMixin, UnpolyViewMixin


def get_view(view, url='/up', **headers):
    request = RequestFactory().get(url, **headers)
    view = view()
    view.setup(request)
    return view


class Note(models.Model):
    name = models.TextField()

    class Meta:
        app_label = 'app_label'
        ordering = ['-level', 'name']


class NoteForm(UnpolyCrispyFormMixin, forms.ModelForm):

    class Meta:
        model = Note
        fields = [
            'name'
        ]


class UnpolyViewMixinTest(SimpleTestCase):

    def test_unpoly_helper(self):

        class UnpolyView(UnpolyViewMixin, TemplateView):
            template_name = 'any_template.html'

        view = get_view(UnpolyView)
        self.assertIsInstance(view.up, Unpoly)


class UnpolyFormViewMixinTest(SimpleTestCase):

    def test_unpoly_target(self):

        class UnpolyView(UnpolyFormViewMixin, TemplateView):
            template_name = 'any_template.html'

        view = get_view(UnpolyView)
        self.assertEqual(view.get_unpoly_target(), settings.MAIN_UP_TARGET)
        context = view.get_context_data(**{})
        self.assertEqual(context['up_target'], settings.MAIN_UP_TARGET)

        not_main_target = '#not_the_main'

        class UnpolyView(UnpolyFormViewMixin, TemplateView):
            template_name = 'any_template.html'
            _unpoly_main_target = not_main_target

        view = get_view(UnpolyView)
        self.assertEqual(view.get_unpoly_target(), not_main_target)
        context = view.get_context_data(**{})
        self.assertEqual(context['up_target'], not_main_target)


class UnpolyCrispyFormVanillaViewMixinTest(SimpleTestCase):

    def test_standard_view_form_attrs(self):
        """
        Views should load unpoly attrs only when request was performed by Unpoly.
        """
        class UnpolyView(UnpolyCrispyFormViewMixin, VanillaCreateView):
            template_name = 'any_template.html'

        view = get_view(UnpolyView)
        self.assertEqual(view.get_form_kwargs(), {})

    def test_unpoly_view_form_attrs(self):
        """
        Views should load unpoly attrs when request was performed by Unpoly.
        """
        class UnpolyView(UnpolyCrispyFormViewMixin, VanillaCreateView):
            template_name = 'any_template.html'

        url_action = '/up'
        view = get_view(UnpolyView, url_action, HTTP_X_UP_VALIDATE='.breadcrumb')
        form_attrs = view.get_form_kwargs()

        self.assertEqual(form_attrs['form_action'], url_action)
        self.assertEqual(form_attrs['up_target'], settings.MAIN_UP_TARGET)
        self.assertEqual(form_attrs['up_fail_target'], settings.MAIN_UP_FAIL_TARGET)

        context = view.get_context_data()
        self.assertEqual(context['up_target'], settings.MAIN_UP_TARGET)
        self.assertEqual(context['up_fail_target'], settings.MAIN_UP_FAIL_TARGET)


class UnpolyCrispyFormDjangoViewMixinTest(SimpleTestCase):

    def test_unpoly_view_form_attrs(self):
        """
        Views should load unpoly attrs when request was performed by Unpoly.
        """
        class UnpolyView(UnpolyCrispyFormViewMixin, DjangoCreateView):
            model = Note
            form_class = NoteForm
            template_name = 'any_template.html'
            object = None

        url_action = '/up'
        view = get_view(UnpolyView, url_action, HTTP_X_UP_VALIDATE='.breadcrumb')
        form_attrs = view.get_form_kwargs()

        self.assertEqual(form_attrs['form_action'], url_action)
        self.assertEqual(form_attrs['up_target'], settings.MAIN_UP_TARGET)
        self.assertEqual(form_attrs['up_fail_target'], settings.MAIN_UP_FAIL_TARGET)

        context = view.get_context_data()
        self.assertEqual(context['up_target'], settings.MAIN_UP_TARGET)
        self.assertEqual(context['up_fail_target'], settings.MAIN_UP_FAIL_TARGET)
