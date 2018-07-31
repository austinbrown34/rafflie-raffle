# myapp/api.py
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash
from tastypie.authentication import ApiKeyAuthentication, MultiAuthentication, SessionAuthentication
from .models import Raffle, UserProfile, RaffleMaster, User, Owner, Product, Winner, Ticket
from tastypie.authorization import Authorization, DjangoAuthorization
from django.conf.urls import url

class RaffleResource(ModelResource):
    class Meta:
        queryset = Raffle.objects.all()
        resource_name = 'raffle'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
        limit=0
        filtering = {
            'status': ALL,
            'featured': ALL
        }
        list_allowed_methods = ['get', 'post']

    def prepend_urls(self):
        """ Add the following array of urls to the GameResource base urls """
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/draw_winners%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('draw_winners'), name="draw_winners"),
        ]

    def draw_winners(self, request, **kwargs):
         """ proxy for the game.start method """
         self.is_authenticated(request)
         # you can do a method check to avoid bad requests
         self.method_check(request, allowed=['get'])

         # create a basic bundle object for self.get_cached_obj_get.
         basic_bundle = self.build_bundle(request=request)

         # using the primary key defined in the url, obtain the game
         raffle = self.cached_obj_get(
             bundle=basic_bundle,
             **self.remove_api_resource_names(kwargs))

         # Return what the method output, tastypie will handle the serialization
         return self.create_response(request, raffle.draw_winners())


class UserProfileResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'userprofile'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())

class RaffleMasterResource(ModelResource):
    class Meta:
        queryset = RaffleMaster.objects.all()
        resource_name = 'rafflemaster'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
        list_allowed_methods = ['get', 'post']

    def prepend_urls(self):
        """ Add the following array of urls to the GameResource base urls """
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/login_tickets%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login_tickets'), name="login_tickets"),
        ]

    def login_tickets(self, request, **kwargs):
         """ proxy for the game.start method """
         self.is_authenticated(request)
         # you can do a method check to avoid bad requests
         self.method_check(request, allowed=['get'])

         # create a basic bundle object for self.get_cached_obj_get.
         basic_bundle = self.build_bundle(request=request)

         # using the primary key defined in the url, obtain the game
         rm = self.cached_obj_get(
             bundle=basic_bundle,
             **self.remove_api_resource_names(kwargs))

         # Return what the method output, tastypie will handle the serialization
         return self.create_response(request, rm.give_all_tickets(100))

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())

class OwnerResource(ModelResource):
    class Meta:
        queryset = Owner.objects.all()
        resource_name = 'owner'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())

class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())

class WinnerResource(ModelResource):
    class Meta:
        queryset = Winner.objects.all()
        resource_name = 'winner'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())

class TicketResource(ModelResource):
    class Meta:
        queryset = Ticket.objects.all()
        resource_name = 'ticket'
        authorization = DjangoAuthorization()
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
