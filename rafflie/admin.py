from django.contrib import admin
from rafflie.models import UserProfile, User, RaffleMaster, Ticket, Owner, Product, Raffle, Winner, AvailableTicket, TicketOpportunity, ShippingInfo

admin.site.register(UserProfile)
admin.site.register(User)
admin.site.register(RaffleMaster)
admin.site.register(Ticket)
admin.site.register(Owner)
admin.site.register(Product)
admin.site.register(Raffle)
admin.site.register(Winner)
admin.site.register(AvailableTicket)
admin.site.register(TicketOpportunity)
admin.site.register(ShippingInfo)
