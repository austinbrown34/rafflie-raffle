from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from rafflie.models import User, Raffle, Product, Owner, Ticket, RaffleMaster, NotEnoughTickets, RaffleNotAcceptingTickets, Winner, NoNegativeTicketsAllowed, OnlyIntegerAmountAllowed, ShippingInfo
from allauth.socialaccount.views import SignupView
from allauth.account.forms import SignupForm, LoginForm
from datetime import datetime
from rafflie.forms import EnterTickets, EnterAddress
# from rafflie.tasks import raffle_now
from allauth.account.utils import complete_signup, send_email_confirmation
from allauth.account import app_settings
import json

class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


class JointLoginSignupView(SignupView):
    form_class = LoginForm
    signup_form = SignupForm
    def __init__(self, **kwargs):
        super(JointLoginSignupView, self).__init__(*kwargs)

    def get_context_data(self, **kwargs):
        ret = super(JointLoginSignupView, self).get_context_data(**kwargs)
        ret['mysignupform1'] = get_form_class(app_settings.FORMS, 'signup', self.signup_form)
        return ret

login = JointLoginSignupView.as_view()




# def raffle(request, raffle_id):
    # context = {
    #     'request': request,
    # }

    # verified = request.session.get('verified', None)
    # resend_verification = request.session.get('resend_verification', None)
    # if resend_verification is not None:
    #     verified = None
    # print verified

    # if winning_message is not None:
    #     form_status = winning_message


    # if a GET (or any other method) we'll create a blank form

    # return HttpResponseSeeOther('/')
    # return render(request, "rafflie/index.html", context)

def raffle(request, raffle_id):
    request.session['raffle_id'] = raffle_id
    return HttpResponseSeeOther('/')

def report(request, raffle_id):
    timenow = None
    diff = None
    raffle = Raffle.objects.get(id=raffle_id)
    raffle.formatted_end_time = raffle.end_time.strftime("%B %d, %Y %H:%M:%S")
    raffle_tickets = Ticket.objects.filter(raffle=raffle)
    raffle_stats = {
        'total_tickets': 0,
        'total_users': 0,
        'average_amount': 0,
        'average_weight': 0,
        'users_percent': 0,
        'most_tickets': 0,
        'least_tickets': 0,
        'highest_percent': 0,
        'lowest_percent': 0,
        'entries': [],
        'json_entries': json.dumps([]),
    }
    diff = (raffle.end_time - timezone.now()).total_seconds()
    # print "diff is: {}".format(diff)
    timenow = timezone.now().strftime("%B %d, %Y %H:%M:%S")
    if len(raffle_tickets) > 0:
        raffle_users = [raffle_ticket.user for raffle_ticket in raffle_tickets]
        print raffle_users
        unique_raffle_users = list(set(raffle_users))
        print unique_raffle_users
        unique_users_entered = len(unique_raffle_users)
        print unique_users_entered

        entry_breakdown = {}

        weight_total = float(0)
        highest_percent = float(0)
        lowest_percent = float(1)
        tickets_total = 0
        for ticket in raffle_tickets:
            tickets_total += ticket.bundle_amount
            if float(ticket.bundle_weight) > highest_percent:
                highest_percent = float(ticket.bundle_weight)
            if float(ticket.bundle_weight) < lowest_percent:
                lowest_percent = float(ticket.bundle_weight)
            weight_total += float(ticket.bundle_weight)
            if str(ticket.user.id) in entry_breakdown:
                if 'bundles' not in entry_breakdown[str(ticket.user.id)]:
                    entry_breakdown[str(ticket.user.id)]['bundles'] = []
                # if ticket.bundle not in entry_breakdown[str(ticket.user.id)]['bundles']:
                if not any(d['bundle'] == ticket.bundle for d in entry_breakdown[str(ticket.user.id)]['bundles']):
                    entry_breakdown[str(ticket.user.id)]['bundles'].append(
                        {
                            'bundle': ticket.bundle,
                            'bundle_weight': round(float(float(ticket.bundle_weight) * 100), 2),
                            'bundle_amount': ticket.bundle_amount,
                            'entered': ticket.entered.__str__(),
                        }
                    )
                total = entry_breakdown[str(ticket.user.id)]['tickets'] + ticket.bundle_amount
                entry_breakdown[str(ticket.user.id)]['tickets'] = total
            else:
                entry_breakdown[str(ticket.user.id)] = {
                    'name': ticket.user.name,
                    'bundles': [{
                        'bundle': ticket.bundle,
                        'bundle_weight': round(float(float(ticket.bundle_weight) * 100), 2),
                        'bundle_amount': ticket.bundle_amount,
                        'entered': ticket.entered.__str__(),
                    }],
                    'tickets': ticket.bundle_amount
                }
                entries = []
                for entry in entry_breakdown:
                    entries.append(entry_breakdown[entry])
                # entry_breakdown[str(ticket.user.id)] = {'tickets': 1}
        print entry_breakdown
        avg_tickets_per_user = float(float(tickets_total)/float(unique_users_entered))
        print avg_tickets_per_user
        all_users = User.objects.count()
        percent_of_users_who_entered = float(float(unique_users_entered)/float(all_users))
        most_tickets_by_one_user = max([ticket['tickets'] for ticket in entry_breakdown.values()])
        least_tickets_by_one_user = min([ticket['tickets'] for ticket in entry_breakdown.values()])
        avg_percent_of_total_available_tickets_entered = float(float(weight_total)/float(len(raffle_tickets)))
        raffle_stats = {
            'total_tickets': tickets_total,
            'total_users': unique_users_entered,
            'average_amount': round(avg_tickets_per_user, 2),
            'average_weight': round(avg_percent_of_total_available_tickets_entered * 100, 2),
            'users_percent': round(percent_of_users_who_entered * 100, 2),
            'most_tickets': most_tickets_by_one_user,
            'least_tickets': least_tickets_by_one_user,
            'highest_percent': round(highest_percent * 100, 2),
            'lowest_percent': round(lowest_percent * 100, 2),
            'entries': entries,
            'json_entries': json.dumps(entries),
        }


    context = {
        'raffle': raffle,
        'raffle_stats': raffle_stats,
        'timenow': timenow,
        'diff': diff,
    }
    return render(request, "rafflie/report.html", context)


def drawing(request):
    winners = None
    if request.method == 'POST':
        print "drawing endpoint:"
        print request.POST
        raffle_id = request.POST['raffle_id']
        # print raffle_id
        # num_of_winners = 1
        raffle = Raffle.objects.get(id=raffle_id)
        print "raffle:"
        print raffle
        # if raffle.num_of_winners is not None:
        #     num_of_winners = raffle.num_of_winners
        # print num_of_winners
        # winners = raffle.draw_winners(num_of_winners=num_of_winners)
        # winners = raffle_now.delay(raffle_id)
        winners = Winner.objects.filter(raffle=raffle)
        print winners
        # winning_message = 'Winner is: '
        # if len(list(winners)) > 1:
        #     winning_message = 'Winners are: '
        # for winner in winners:
        #     winning_message += winner.user.name + ', '

        # winning_message = winning_message.strip(', ')
        # request.session['winning_message'] = winning_message
        print {"found_winners": str(len(winners))}
    return HttpResponse(json.dumps({"found_winners": str(len(winners))}), content_type='application/json')
    # return HttpResponseSeeOther('/')

def verify(request):
    send_email_confirmation(request, request.user, signup=True)
    request.session['resend_verification'] = None
    request.session['verified'] = None
    return HttpResponseSeeOther('/')

def resend_verification(request):
    request.session['resend_verification'] = True
    return HttpResponseSeeOther('/')

def verified(request, key):
    print "this was the request"
    print request
    print "key was:"
    print key
    request.session['verified'] = key
    return HttpResponseSeeOther('/')

def cancelled(request):
    return HttpResponseSeeOther('/')


def share(request):
    from rafflie.tasks import ShareTask
    if request.method == 'POST':
        print "made it to the share"
        # raffle_id = request.POST['raffle_id']
        # print raffle_id
        # num_of_winners = 1
        # raffle = Raffle.objects.get(id=raffle_id)
        # if raffle.num_of_winners is not None:
        #     num_of_winners = raffle.num_of_winners
        # print num_of_winners
        # winners = raffle.draw_winners(num_of_winners=num_of_winners)
        # winners = raffle_now.delay(raffle_id)
        raffle_id = request.POST['raffle_id']
        print raffle_id
        if request.user.is_authenticated:
            raffle_user = User.objects.filter(email=request.user.email)[0]
        print raffle_user.id

        ShareTask.delay(raffle_user.id)

        # winning_message = 'Winner is: '
        # if len(list(winners)) > 1:
        #     winning_message = 'Winners are: '
        # for winner in winners:
        #     winning_message += winner.user.name + ', '
        # winning_message = winning_message.strip(', ')
        # request.session['winning_message'] = winning_message

    return HttpResponseSeeOther('/')


def enter_tickets(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EnterTickets(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if request.user.is_authenticated:
                raffle_user = User.objects.filter(email=request.user.email)[0]
                raffle_id = request.session.get('raffle_id', None)
                if raffle_id is None:
                    print "raffle id is none"
                    raffle = Raffle.objects.filter(featured=True)[0]
                else:
                    print "raffle id is: {}".format(raffle_id)
                    raffle = Raffle.objects.get(id=raffle_id)
                tickets = form.cleaned_data['tickets']
                print raffle_user.tickets
                print tickets
                try:
                    result = raffle_user.enter_tickets(raffle=raffle, amount=tickets)
                    form_status = 'Tickets Entered!'
                except NotEnoughTickets as e:
                    form_status = str(e)
                except RaffleNotAcceptingTickets as x:
                    form_status = str(x)
                except NoNegativeTicketsAllowed as n:
                    form_status = str(n)
                except OnlyIntegerAmountAllowed as o:
                    form_status = str(o)

            else:
                form_status = 'You must be logged in to enter tickets.'
    return HttpResponseSeeOther('/')


def enter_address(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EnterAddress(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            if request.user.is_authenticated:
                raffle_user = User.objects.filter(email=request.user.email)[0]
                raffle_id = request.session.get('raffle_id', None)
                if raffle_id is None:
                    print "raffle id is none"
                    raffle = Raffle.objects.filter(featured=True)[0]
                else:
                    print "raffle id is: {}".format(raffle_id)
                    raffle = Raffle.objects.get(id=raffle_id)
                # if raffle_id is None:
                #     print "raffle id is none"
                #     raffle = Raffle.objects.filter(featured=True)[0]
                # else:
                #     print "raffle id is: {}".format(raffle_id)
                #     raffle = Raffle.objects.get(id=raffle_id)
                fullname = form.cleaned_data['fullname']
                address = form.cleaned_data['address']
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                zipcode = form.cleaned_data['zipcode']
                # print raffle_user.tickets
                print fullname
                print address
                print city
                print state
                print zipcode
                # raffle = Raffle.objects.get(id=raffle_id)

                winners = Winner.objects.filter(raffle=raffle, user=raffle_user)
                shipping_info = ShippingInfo.objects.create(fullname=fullname, address=address, city=city, state=state, zipcode=zipcode)
                for winner in winners:
                    winner.shipping_info = shipping_info
                    Winner.save(winner)



                # try:
                #     result = raffle_user.enter_tickets(raffle=raffle, amount=tickets)
                #     form_status = 'Tickets Entered!'
                # except NotEnoughTickets as e:
                #     form_status = str(e)
                # except RaffleNotAcceptingTickets as x:
                #     form_status = str(x)
                # except NoNegativeTicketsAllowed as n:
                #     form_status = str(n)
                # except OnlyIntegerAmountAllowed as o:
                #     form_status = str(o)
        request.session['address_set'] = True
        # request.session.set('address_set', True)
    return HttpResponseSeeOther('/')


def index(request, raffle_id=None):
    winners = None
    user_is_winner = None
    raffle_user = None
    raffle = None
    form = None
    form_status = None
    timenow = None
    diff = None
    verified = None
    resend_verification = None
    owner_logo = None
    address_set = request.session.get('address_set', False)



    raffle_ids = list(Raffle.objects.all().values_list('id', flat=True))
    raffle_images = []
    raffle_logos = []
    for raffle_id in raffle_ids:
        r = Raffle.objects.get(id=raffle_id)
        raffle_images.append(str(r.product.image2))
        raffle_logos.append(str(r.owner.logo))

    form = EnterTickets()


    if request.user.is_authenticated:
        raffle_user = User.objects.filter(email=request.user.email)[0]

    try:
        raffle_id = request.session.get('raffle_id', None)
        if raffle_id is None:
            print "raffle id is none"
            raffle = Raffle.objects.filter(featured=True)[0]
        else:
            print "raffle id is: {}".format(raffle_id)
            raffle = Raffle.objects.get(id=raffle_id)
        print "raffle is: "
        print raffle
        owner_logo = raffle.owner.logo
        raffle.formatted_end_time = raffle.end_time.strftime("%B %d, %Y %H:%M:%S")
        diff = (raffle.end_time - timezone.now()).total_seconds()
        # print "diff is: {}".format(diff)
        timenow = timezone.now().strftime("%B %d, %Y %H:%M:%S")
        winners = Winner.objects.filter(raffle=raffle)
        if not winners:
            winners = None
        else:
            # print "No Winners"

            if len(list(winners)) > 0:


                winning_message = 'Winner is: '
                if len(list(winners)) > 1:
                    winning_message = 'Winners are: '
                for winner in winners:
                    if raffle_user is not None:
                        if winner.user.id == raffle_user.id:

                            user_is_winner = True
                            if not address_set and winner.shipping_info is not None:
                                address_set = True
                    winning_message += winner.user.name + ', '
                winning_message = winning_message.strip(', ')
                form_status = winning_message
    except IndexError as e:
        print str(e)

    context = {
        'user_is_winner': user_is_winner,
        'raffle_user': raffle_user,
        'raffle': raffle,
        'form': form,
        'winners': winners,
        'form_status': form_status,
        'timenow': timenow,
        'diff': diff,
        'verified': verified,
        'resend_verification': resend_verification,
        'owner_logo': owner_logo,
        'raffle_ids': raffle_ids,
        'raffle_images': json.dumps(raffle_images),
        'raffle_logos': json.dumps(raffle_logos),
        'address_set': address_set
    }
    # print request.user.is_authenticated
    # if not User.objects.filter(email=request.user.email).exists():
    #     if request.user.first_name != '' and request.user.last_name != '':
    #         name = '{} {}'.format(request.user.first_name, request.user.last_name)
    #     else:
    #         name = request.user.username
    #     raffle_user = User(name=name, email=request.user.email)
    #     User.save(raffle_user)
    #     print 'New User ID: {}'.format(raffle_user.id)
    return render(request, "rafflie/index.html", context)
