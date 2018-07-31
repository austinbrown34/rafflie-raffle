import os

from django.core.wsgi import get_wsgi_application
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapp.settings'
application = get_wsgi_application()

from rafflie.models import Raffle

new_end_time = timezone.now() + timezone.timedelta(days=7)

raffles = Raffle.objects.all()
for raffle in raffles:
    raffle.status = 1
    raffle.end_time = new_end_time
    Raffle.save(raffle)
