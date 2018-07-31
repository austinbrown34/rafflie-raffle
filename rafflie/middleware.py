from django.utils import timezone

from rafflie.models import User


class UpdateLastActivityMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        if request.user.is_authenticated():
            User.objects.filter(user__id=request.user.id) \
                           .update(last_activity=timezone.now())
