django-unpoly
=============

What it does
------------

``unpoly`` is a reusable app for [Django](https://www.djangoproject.com/) implementing a Django-flavored
[Unpoly v2 Server Protocol](https://unpoly.com/up.protocol).

It provides:

1. A middleware which adds `is_unpoly` `unpoly_target`, and `unpoly_validate` methods to the request object. 

2. A view mixin classes support both [Django Generic Views](https://docs.djangoproject.com/en/dev/topics/class-based-views/generic-display/) and [Vanilla Views](http://django-vanilla-views.org/). 

3. A Form mixin class for [Crispy Forms](https://django-crispy-forms.readthedocs.io).


Installation
------------

  pip install unpoly_django

Configuration
-------------
You need to add ``unpoly.middleware.UnpolyMiddleware`` to your ``MIDDLEWARE``.

To install all the middleware, you want something like:


```python
MIDDLEWARE = (
    # ...
    'unpoly.middleware.UnpolyMiddleware',
    # ...
)
```

Settings
--------

If using the View mixins following constants to settings.py:

```python
MAIN_UP_TARGET = '#your_main_up_target'
MAIN_UP_FAIL_TARGET = '#your_main_upfail_target'

DEFAULT_UP_ERROR_TEMPLATE = 'your-unpoly-error-template.html'

# Default Templates for various Unpoly layers.
# Override on individual View attributes.
UNPOLY_MODAL_TEMPLATE = 'your-unpoly-modal-template.html'
UNPOLY_DRAWER_TEMPLATE = 'your-unpoly-drawer-template.html'
UNPOLY_POPUP_TEMPLATE = 'your-unpoly-popup-template.html'
UNPOLY_COVER_TEMPLATE = 'your-unpoly-cover-template.html'

# Routing URL kwarg set when an optimized response is to be sent
OPTIMIZED_SUCCESS_RESPONSE = 'optimized_success_response'

DEFAULT_ERROR_VIEW = 'appname:error_view_name'
```

CSRF Token
----------

Ensure that the `csrf_token` meta tag is included in the head section of your templates

```html
<meta name="csrf-token" content="{{ csrf_token }}" />
```

View Mixins
-----------

View mixin classes add hooks and properties for sending optimized server
responses to the frontend.

Add view mixin classes to Django's Generic views, or Vanilla Views:

```python
from django.views.generic import FormView, TemplateView
from unpoly.views import UnpolyViewMixin, UnpolyFormViewMixin, UnpolyCrispyFormViewMixin


class YourTemplateView(UnpolyViewMixin, TemplateView):
    pass

class YourFormView(UnpolyViewMixin, FormView):
    pass

class YourCrispyFormView(UnpolyCrispyFormViewMixin, FormView):
    pass
```

Crispy Form Mixin
-----------------

The Crispy Form mixin can be used when form mixins are used, which enables passing
`up-target`, `up-layer`, `up-fail-layer` and `up-fail-target` params from views to forms:

```python
from django.forms import ModelForm
from unpoly.forms import UnpolyCrispyFormMixin

class UnpolyCrispyForm(UnpolyCrispyFormMixin, ModelForm):
    pass
```


Running the tests
-----------------

If you have a cloned copy, run::

  python3 runtests.py

Contributing
------------

Contributions welcome! The project lives in the Github repo at [thinkwelltwd/unpoly_django](https://github.com/thinkwelltwd/unpoly_django/)
repository.

Bug reports and feature requests can be filed on the repository's [issue tracker](https://github.com/thinkwelltwd/unpoly_django/issues/).


License
-------

Released under the [MIT License](https://mit-license.org/). There's should be a ``LICENSE`` file in the root of the repository.
