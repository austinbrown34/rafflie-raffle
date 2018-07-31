from django.conf.urls import url, include
from rafflie import views
from allauth.account import views as allauthviews
from django.contrib.auth import views as auth_views

urlpatterns = [
    # url(r'^accounts/confirm-email/(?P<key>[-:\w]+)/$', views.verified, name='verified'),
    # url(r'^accounts/resend_verification/$', views.verify, name='verify'),
    # url(r'^accounts/email/$', views.resend_verification, name='resend_verification'),
    url(r'^accounts/social/login/cancelled/$', views.cancelled, name='cancelled'),
    url(r'^accounts/social/confirm-email/', views.verified, name='verified'),
    url(r'^accounts/social/confirm-email/*/$', views.verified, name='verified'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^drawing/', views.drawing, name='drawing'),
    url(r'^enter_tickets/', views.enter_tickets, name='enter_tickets'),
    url(r'^enter_address/', views.enter_address, name='enter_address'),
    url(r'^$', views.index, name='index'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'}),
    url(r'^share/', views.share, name='share'),
    url(r'^raffle/(?P<raffle_id>\d+)/$', views.raffle, name='raffle'),
    url(r'^raffle/(?P<raffle_id>\d+)/report/$', views.report, name='report'),

]
