"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from rafflie import views
from rafflie.api import RaffleResource, UserProfileResource, RaffleMasterResource, UserResource, OwnerResource, ProductResource, WinnerResource, TicketResource

raffle_resource = RaffleResource()
userprofile_resource = UserProfileResource()
rafflemaster_resource = RaffleMasterResource()
user_resource = UserResource()
owner_resource = OwnerResource()
product_resource = ProductResource()
winner_resource = WinnerResource()
ticket_resource = TicketResource()

admin.autodiscover()

urlpatterns = [


    # url(r'^accounts/login/$', auth_views.login),
    url('^', include('django.contrib.auth.urls')),
    # url(r'^accounts/confirm-email/(?P<key>[-:\w]+)/$', views.verified, name='verified'),
    # url(r'^accounts/resend_verification/$', views.verify, name='verify'),
    # url(r'^accounts/email/$', views.resend_verification, name='resend_verification'),
    url(r'^accounts/', include('allauth.account.urls')),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'}),
    url(r'^', include('rafflie.urls', namespace="rafflie")),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/social/login/cancelled/$', views.cancelled, name='cancelled'),
    url(r'^accounts/social/confirm-email/', views.verified, name='verified'),
    url(r'^accounts/social/confirm-email/*/$', views.verified, name='verified'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^api/', include(raffle_resource.urls)),
    url(r'^api/', include(userprofile_resource.urls)),
    url(r'^api/', include(rafflemaster_resource.urls)),
    url(r'^api/', include(user_resource.urls)),
    url(r'^api/', include(owner_resource.urls)),
    url(r'^api/', include(product_resource.urls)),
    url(r'^api/', include(winner_resource.urls)),
    url(r'^api/', include(ticket_resource.urls)),
]
