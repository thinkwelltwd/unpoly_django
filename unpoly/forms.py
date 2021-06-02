from crispy_forms.helper import FormHelper


class UnpolyCrispyFormMixin:
    """
    For projects using Crispy Forms, use this mixin class to have
    Unpoly attributes injected into the form tag.
    """

    def __init__(self, *args, **kwargs: dict) -> None:
        """Set any Unpoly attributes on Crispy FormHelper.

        Use view mixins to set attributes in view.get_form method
        """
        self.form_action: str = kwargs.pop('form_action', '')
        self.multi_layer: bool = kwargs.pop('multi_layer', False)
        self.up_target: str = kwargs.pop('up_target', '')
        self.up_fail_target: str = kwargs.pop('up_fail_target', '')
        self.up_validate: str = kwargs.pop('up_validate', '')

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        if self.form_action:
            self.helper.form_action = self.form_action
        self._set_unpoly_attrs()

    def unpoly_form_attrs(self) -> dict:
        """Unpoly html attributes that should be set on the form.

        Override on subclasses to customize.
        """
        if not self.up_target:
            return {}

        unpoly_attrs = {
            'up-target': self.up_target,
            'up-layer': 'root current',
            'up-fail-layer': 'current',
            'up-fail-target': self.up_fail_target,
        }
        if self.multi_layer:
            unpoly_attrs['up-layer'] = 'current'

        return unpoly_attrs

    def _set_unpoly_attrs(self):
        """Set Unpoly attributes on Crispy FormHelper.
        """
        unpoly_attrs = self.unpoly_form_attrs()

        if not unpoly_attrs:
            return

        self.helper.attrs.update(unpoly_attrs)


__all__ = [
    'UnpolyCrispyFormMixin',
]
