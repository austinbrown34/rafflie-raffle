from django.dispatch.dispatcher import Signal
from django.db.models.signals import post_save
from actstream import action

from allauth.account.signals import user_logged_in
import django.dispatch
from django.dispatch import receiver
from django.contrib.auth import user_logged_out


def my_handler(sender, instance, created, **kwargs):
    action.send(instance, verb='was saved')


@receiver(user_logged_in)
def user_logged_in(request, user, **kwargs):
    action.send(request.user, verb='Logged in')


@receiver(user_logged_out)
def user_logged_out(request, user, **kwargs):
    action.send(request.user, verb='Logged out')


tickets_received = Signal(providing_args=['user', 'amount'])

def tickets_received_handler(sender, user, amount, **kwargs):
    print "tickets received"
    action.send(sender, verb='gave ' + str(amount) + ' tickets to ', target=user)

tickets_received.connect(tickets_received_handler)

tickets_entered = Signal(providing_args=['amount', 'raffle'])

def tickets_entered_handler(sender, amount, raffle, **kwargs):
    print "tickets entered"
    action.send(sender, verb='entered ' + str(amount) + ' tickets into ', target=raffle)

tickets_entered.connect(tickets_entered_handler)

tickets_redeemed = Signal(providing_args=['amount', 'ticket_opportunity'])

def tickets_redeemed_handler(sender, amount, ticket_opportunity, **kwargs):
    print "tickets redeemed"
    action.send(sender, verb='redeemed ' + str(amount) + ' tickets from ', target=ticket_opportunity)

tickets_redeemed.connect(tickets_redeemed_handler)

raffle_live = Signal()

def raffle_live_handler(sender, **kwargs):
    print "raffle goes live"
    action.send(sender, verb='went live')

raffle_live.connect(raffle_live_handler)

raffle_shutdown = Signal()

def raffle_shutdown_handler(sender, **kwargs):
    print "raffle has shutdown"
    action.send(sender, verb='has shutdown')

raffle_shutdown.connect(raffle_shutdown_handler)

raffle_draw = Signal(providing_args=['winners'])

def raffle_draw_handler(sender, winners, **kwargs):
    print "raffle drawing"
    action.send(sender, verb='drew ' + str(len(winners)) + ' winners')
    for winner in winners:
        action.send(sender, verb='drew', target=winner)

raffle_draw.connect(raffle_draw_handler)
