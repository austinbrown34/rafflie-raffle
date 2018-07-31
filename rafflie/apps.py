from __future__ import unicode_literals

from django.apps import AppConfig
#


class RafflieConfig(AppConfig):
    name = 'rafflie'
    def ready(self):
        from actstream import registry
        import signals
        registry.register(
            self.get_model('UserProfile'),
            self.get_model('TicketOpportunity'),
            self.get_model('RaffleMaster'),
            self.get_model('User'),
            self.get_model('AvailableTicket'),
            self.get_model('Owner'),
            self.get_model('Product'),
            self.get_model('Raffle'),
            self.get_model('Winner'),
            self.get_model('Ticket')
        )
