from __future__ import unicode_literals
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.db import models, transaction
from django.db.models.aggregates import Count
from random import randint
from allauth.socialaccount.models import SocialAccount
import hashlib

from rafflie.signals import tickets_received, tickets_entered, tickets_redeemed, raffle_live, raffle_shutdown, raffle_draw

from tastypie.models import create_api_key
from actstream import registry
from actstream import action
from model_utils import FieldTracker
import datetime
from itertools import repeat



models.signals.post_save.connect(create_api_key, sender=User)


class IncorrectNumOfWinners(Exception):
    pass

class OnlyIntegerAmountAllowed(Exception):
    pass


class NoNegativeTicketsAllowed(Exception):
    pass


class NotEnoughTickets(Exception):
    pass


class WinnersAlreadyDrawn(Exception):
    pass


class RaffleNotActive(Exception):
    pass

class RaffleNotAcceptingTickets(Exception):
    pass

@receiver(post_save, sender=User)
def create_raffle_user(sender, instance, **kwargs):
    if not User.objects.filter(email=instance.email).exists():
        if instance.first_name and instance.last_name:
            name = '{} {}'.format(instance.first_name, instance.last_name)
        else:
            name = instance.username
        raffle_user = User(name=name, email=instance.email, tickets=100)
        User.save(raffle_user)

        print 'New User ID: {}'.format(raffle_user.id)
        action.send(instance, verb='was created')


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    about_me = models.TextField(null=True, blank=True)


    def __unicode__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    def profile_image_url(self):
        """
        Return the URL for the user's Facebook icon if the user is logged in via Facebook,
        otherwise return the user's Gravatar URL
        """

        fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')

        if len(fb_uid):
            return "http://graph.facebook.com/{}/picture?width=53&height=53".format(fb_uid[0].uid)

        return "http://www.gravatar.com/avatar/{}?s=53".format(
            hashlib.md5(self.user.email).hexdigest())

    def account_verified(self):
        """
        If the user is logged in and has verified hisser email address, return True,
        otherwise return False
        """
        result = EmailAddress.objects.filter(email=self.user.email)
        if len(result):
            return result[0].verified
        return False



User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class TicketOpportunity(models.Model):
    name = models.CharField(max_length=200)
    tickets = models.IntegerField(default=0)
    full_description = models.CharField(max_length=500, blank=True, null=True)
    status = models.IntegerField(default=0)

    def __str__(self):
        return '{}: {}: {}'.format(self.name, self.tickets, self.status)

class RaffleMaster(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)

    def give_tickets(self, user, amount):

        user.add_tickets(amount)
        User.save(user)
        tickets_received.send(sender=self, user=user, amount=amount)

    def give_all_tickets(self, amount):
        users = list(User.objects.all())
        ticket_opp, created = TicketOpportunity.objects.get_or_create(name="Login Tickets", tickets=amount, full_description='Daily tickets just for the heck of it!', status=1)
        for user in users:
            available_tickets = list(AvailableTicket.objects.filter(user=user, ticket_opportunity=ticket_opp))
            if available_tickets:
                available_ticket = available_tickets[0]
                available_ticket.status == 1
            else:
                available_ticket = AvailableTicket(
                    ticket_opportunity=ticket_opp,
                    user=user,
                    status=1
                )
            AvailableTicket.save(available_ticket)
            day_ago = (timezone.now() - datetime.timedelta(days=1))
            print("Giving away tickets!")
            if user.last_activity > day_ago:
                print('Awarding: {}'.format(user))
                self.give_tickets(user=user, amount=ticket_opp.tickets)
            User.save(user)
            TicketOpportunity.save(ticket_opp)
        return {"status": "OK", "msg": "Successfully Gave Login Tickets"}


    def __str__(self):
        return '{}: {}'.format(self.name, self.email)



class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    tickets = models.IntegerField(default=0)
    last_activity = models.DateTimeField(default=timezone.now)


    def get_ticket_balance(self):
        return self.tickets

    def subtract_tickets(self, amount):
        self.tickets -= amount

    def add_tickets(self, amount):
        self.tickets += amount

    def enter_tickets(self, raffle, amount):
        print "user tickets:"
        print self.tickets
        print "amount:"
        print amount
        try:
            amount = int(amount)
        except ValueError:
            raise OnlyIntegerAmountAllowed(
                'Ticket amount must be an integer'
            )
        if amount < 0:
            raise NoNegativeTicketsAllowed(
                'You cannot enter a negative number of tickets.'
            )
        if amount > self.tickets:
            raise NotEnoughTickets(
                'You cannot enter more tickets than you have.'
            )
        elif raffle.status != 1:
            raise RaffleNotAcceptingTickets(
                'This raffle is not currently accepting tickets.'
            )
        else:

            tickets_before_entry = self.tickets
            entered = timezone.now()
            ticket = Ticket(user=self)
            ticket.assign_raffle(raffle, entered)
            ticket.assign_bundle_props(amount, tickets_before_entry, entered)
            Ticket.save(ticket)

            self.subtract_tickets(amount)
            User.save(self)
            raffle.add_tickets(amount)
            Raffle.save(raffle)
            tickets_entered.send(sender=self, amount=amount, raffle=raffle)

    def redeem_available_tickets(self, ticket_opportunity):
        available_tickets = list(AvailableTicket.objects.filter(ticket_opportunity=ticket_opportunity, status=1, ticket_opportunity__status=1))
        ticket_counter = 0
        for opportunity in available_tickets:
            ticket_counter += opportunity.ticket_opportunity.tickets
        rm = RaffleMaster.objects.first()
        rm.give_tickets(self, ticket_counter)
        RaffleMaster.save(rm)
        tickets_redeemed.send(sender=self, amount=ticket_counter, ticket_opportunity=ticket_opportunity)

    def __str__(self):
        return '{}: {}'.format(self.name, self.email)



class AvailableTicket(models.Model):
    ticket_opportunity = models.ForeignKey(TicketOpportunity, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)

    def __str__(self):
        return '{}: {}: {}'.format(self.ticket_opportunity.name, self.user.email, self.status)



class Owner(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=1000, blank=True, null=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    logo = models.CharField(max_length=1000, blank=True, null=True)


    def __str__(self):
        return '{}: {}'.format(self.name, self.email)



class Product(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    image1 = models.CharField(max_length=1000, blank=True, null=True)
    image2 = models.CharField(max_length=1000, blank=True, null=True)
    image3 = models.CharField(max_length=1000, blank=True, null=True)
    full_description = models.CharField(max_length=1000, blank=True, null=True)
    key_features = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return '{}: Owned by: {}'.format(self.name, self.owner.name)



class Raffle(models.Model):
    name = models.CharField(max_length=200)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    tickets = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    short_description = models.CharField(max_length=1000, blank=True, null=True)
    num_of_winners = models.IntegerField(blank=True, null=True)
    est_value = models.CharField(max_length=200, blank=True, null=True)
    fine_print = models.CharField(max_length=1000, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    parent = models.IntegerField(blank=True, null=True)
    tracker = FieldTracker()
    def duplicate(self):
        if self.parent:
            my_parent = self.parent
        else:
            my_parent = self.id
        raffle_sibling = Raffle(
            name=self.name,
            product=self.product,
            owner=self.owner,
            fine_print=self.fine_print,
            short_description=self.short_description,
            num_of_winners=self.num_of_winners,
            est_value=self.est_value,
            parent=my_parent
        )
        Raffle.save(raffle_sibling)
        return raffle_sibling

    def get_ticket_count(self):
        return self.tickets

    def go_live(self):
        self.status = 1
        raffle_live.send(sender=self)

    def shutdown(self):
        self.status = 0
        raffle_shutdown.send(sender=self)

    def add_tickets(self, amount):
        self.tickets += amount

    @transaction.atomic
    def draw_winners(self, num_of_winners=None):
        if num_of_winners is None:
            num_of_winners = self.num_of_winners
        winners = list(Winner.objects.filter(raffle=self))

        if self.num_of_winners != num_of_winners:
            raise IncorrectNumOfWinners('Incorrect number of winners.')
        elif winners:
            raise WinnersAlreadyDrawn('Winners have already been drawn.')
        elif self.status != 1:
            raise RaffleNotActive('Raffle is not currently active.')
        else:
            winners = []
            tickets = Ticket.objects.filter(raffle=self, status=1)
            tickets_list = list(tickets)
            num_of_entries = len(tickets)
            print "num of entries: "
            print num_of_entries
            print "num of tickets"
            total_tickets = 0
            entries_list = []
            for ticket in tickets_list:
                total_tickets += ticket.bundle_amount
                entries_list.extend(repeat(ticket, ticket.bundle_amount))
            print total_tickets
            num_of_winners = self.num_of_winners
            for x in range(num_of_winners):
                random_index = randint(0, total_tickets - 1)
                winner = entries_list[random_index]
                win = Winner(user=winner.user, raffle=self)
                Winner.save(win)
                print 'Winner is: {}'.format(winner.user)
                winners.append(winner)
                winner.expire()
                Ticket.save(winner)
                entries_list.pop(random_index)
                num_of_entries -= 1
            self.shutdown()
            Raffle.save(self)
            raffle_draw.send(sender=self, winners=winners)
        return winners



    def __str__(self):
        return '{}: Product: {}, Owner: {}'.format(
            self.name,
            self.product.name,
            self.owner.name
        )


@receiver(post_save, sender=Raffle)
def update_countdowns(sender, instance, **kwargs):
    if instance.featured:
        print 'woooooot featured!'
        other_featured_raffles = Raffle.objects.filter(featured=True)
        for raffle in other_featured_raffles:
            if raffle.id != instance.id:
                raffle.featured = False
                Raffle.save(raffle)


class ShippingInfo(models.Model):
    fullname = models.CharField(null=True, blank=True, max_length=500)
    address = models.CharField(null=True, blank=True, max_length=500)
    city = models.CharField(null=True, blank=True, max_length=500)
    state = models.CharField(null=True, blank=True, max_length=500)
    zipcode = models.CharField(null=True, blank=True, max_length=500)

    def __str__(self):
        return '{}:{},{},{},{}'.format(self.fullname, self.address, self.city, self.state, self.zipcode)

class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE)
    shipping_info = models.ForeignKey(ShippingInfo, blank=True, null=True)


    def __str__(self):
        return '{}: Winner of Raffle: {}'.format(self.user.name, self.raffle.name)




class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(default=1)
    entered = models.DateTimeField(null=True, blank=True)
    bundle = models.CharField(null=True, blank=True, max_length=500)
    bundle_weight = models.CharField(null=True, blank=True, max_length=500)
    bundle_amount = models.IntegerField(null=True, blank=True)

    def expire(self):
        self.status = 0

    def assign_raffle(self, raffle, entered):
        self.raffle = raffle
        self.entered = entered

    def assign_bundle_props(self, bundle_amount, previous_total, entered):
        self.bundle_amount = bundle_amount
        self.bundle_weight = str(float(bundle_amount)/float(previous_total))
        self.bundle = '{}-{}-{}-{}'.format(
            self.raffle.id,
            self.user.id,
            self.bundle_amount,
            entered
        )
        print 'assign bundle props:'
        print self.bundle_amount
        print previous_total
        print self.bundle_weight
        print self.bundle

    def __str__(self):
        return '{}: User: {}, Raffle: {}'.format(
            self.id,
            self.user,
            self.raffle
        )
