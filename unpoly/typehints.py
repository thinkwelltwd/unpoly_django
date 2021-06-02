from django.http import HttpRequest


class UnpolyHttpRequest(HttpRequest):
    """
    HttpRequest class for using as type hint to Django Generic Class-based Views,
    Vanilla views, and View Mixin classes.

    from django.views.generic import CreateView
    class UserCreate(CreateView):
        request: UnpolyHttpRequest
    """

    def is_unpoly(self) -> bool:
        return False

    def unpoly_target(self) -> str:
        return ''

    def unpoly_validate(self) -> bool:
        return False


__all__ = [
    'UnpolyHttpRequest',
]
