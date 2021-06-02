from django import forms
from django.test import SimpleTestCase

from unpoly.forms import UnpolyCrispyFormMixin
from .settings import MAIN_UP_TARGET, MAIN_UP_FAIL_TARGET


class UnpolyForm(UnpolyCrispyFormMixin, forms.Form):
    name = forms.CharField()


class UnpolyCrispyFormMixinTest(SimpleTestCase):

    def test_unpoly_form_attrs(self):

        form = UnpolyForm(
            form_action='/up',
            multi_layer=False,
            up_target=MAIN_UP_TARGET,
            up_fail_target=MAIN_UP_FAIL_TARGET,
            up_validate='.name',
        )

        self.assertEqual(form.helper.form_action, '/up')
        self.assertEqual(form.helper.attrs['up-target'], MAIN_UP_TARGET)
        self.assertEqual(form.helper.attrs['up-fail-target'], MAIN_UP_FAIL_TARGET)

    def test_unpoly_multi_layerform_attrs(self):
        """
        up-layer should be changed when multiple layers are opened
        """
        form = UnpolyForm(
            form_action='/up',
            multi_layer=True,
            up_target=MAIN_UP_TARGET,
            up_fail_target=MAIN_UP_FAIL_TARGET,
            up_validate='.name',
        )

        self.assertEqual(form.helper.attrs['up-layer'], 'current')
