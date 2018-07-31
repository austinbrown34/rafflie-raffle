# from celery import Celery, current_app
# from celery.schedules import crontab
# from celery.utils.log import get_task_logger
# from celery.task import periodic_task, Task
# from datetime import timedelta
# from rafflie.models import User, RaffleMaster, TicketOpportunity, AvailableTicket, Raffle, WinnersAlreadyDrawn, RaffleNotActive, Ticket
# import os
# from django.db import transaction
# from django.utils import timezone
# from django.core.mail import EmailMessage
# import datetime
# import urlparse
# from actstream import registry
# from actstream import action
#
# app = Celery('webapp', broker=os.environ['REDIS_URL'])
# logger = get_task_logger(__name__)
#
# import redis
# app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
#                 CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])
#
# REDIS_URL = os.getenv('REDIS_URL')
#
# urlparse.uses_netloc.append('redis')
# url = urlparse.urlparse(REDIS_URL)
# # conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)
#
# REDIS_CLIENT = redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)
#
# def only_one(function=None, key="", timeout=None):
#     """Enforce only one celery task at a time."""
#
#     def _dec(run_func):
#         """Decorator."""
#
#         def _caller(*args, **kwargs):
#             """Caller."""
#             ret_value = None
#             have_lock = False
#             lock = REDIS_CLIENT.lock(key, timeout=timeout)
#             try:
#                 have_lock = lock.acquire(blocking=False)
#                 if have_lock:
#                     ret_value = run_func(*args, **kwargs)
#             finally:
#                 if have_lock:
#                     lock.release()
#
#             return ret_value
#
#         return _caller
#
#     return _dec(function) if function is not None else _dec
#
#
# class RaffleTask(Task):
#     """A task."""
#     Task.name = 'rafflie.tasks.RaffleTask'
#     @only_one(key="SingleTask", timeout=60 * 1)
#     def run(self, raffle_id, **kwargs):
#         """Run task."""
#         print("Acquired lock for up to 5 minutes and ran task!")
#         raffle_now_tasks = current_app.tasks['rafflie.tasks.raffle_now']
#         print "raffle tasks in the queue:"
#         print raffle_now_tasks
#         raffle = Raffle.objects.get(id=raffle_id)
#         winners = None
#         num_of_winners = 1
#         if raffle.num_of_winners is not None:
#             num_of_winners = raffle.num_of_winners
#         winners = raffle.draw_winners(num_of_winners=num_of_winners)
#         tickets_entered = Ticket.objects.filter(raffle=raffle)
#         if tickets_entered:
#             users_entered = list(set([rt.user for rt in tickets_entered]))
#             win = []
#             lose = []
#             user_winners = [w.user for w in winners]
#             for user in users_entered:
#                 if user in user_winners:
#                     win.append(user.email)
#                 else:
#                     lose.append(user.email)
#             print winners
#             print user_winners
#             # message_win = ('[Rafflie] You Won {}!'.format(raffle.name), 'Congratulations!  You took a shot, and it paid off!  Visit rafflie.com to claim your prize and help us make sure it gets to you. Further instructions may be emailed to you soon, so keep an eye out for us!', 'team@rafflie.com', bcc=win)
#             # message_lose = ('[Rafflie] Nice Try, but were not a winner of {}'.format(raffle.name), 'Thanks for playing!  No worries good friend, there are new raffles and more free tickets coming your way soon.  Visit rafflie.com often to make sure you always get your free daily tickets.  See you soon!', 'team@rafflie.com', bcc=lose)
#             # delivered = send_mail((message_win, message_lose), fail_silently=False)
#             win_email = EmailMessage(
#                 '[Rafflie] You Won {}!'.format(raffle.name),
#                 'Congratulations!  You took a shot, and it paid off!  Visit rafflie.com to claim your prize and help us make sure it gets to you. Further instructions may be emailed to you soon, so keep an eye out for us!',
#                 'team@rafflie.com',
#                 bcc=win
#             )
#             lose_email = EmailMessage(
#                 '[Rafflie] Nice Try, but you were not a winner of {}'.format(raffle.name),
#                 'Thanks for playing!  No worries good friend, there are new raffles and more free tickets coming your way soon.  Visit rafflie.com often to make sure you always get your free daily tickets.  See you soon!',
#                 'team@rafflie.com',
#                 bcc=lose
#             )
#             win_email.send()
#             lose_email.send()
#             # print "Successfully delivered {} emails.".format(delivered)
#         return winners
#
#
# class ShareTask(Task):
#     Task.name = 'rafflie.tasks.ShareTask'
#     def run(self, user_id, **kwargs):
#         rm = RaffleMaster.objects.first()
#         user = User.objects.get(id=user_id)
#         ticket_opp, created = TicketOpportunity.objects.get_or_create(name="Share Tickets", tickets=20, full_description='Daily tickets just for sharing!', status=1)
#         available_tickets = list(AvailableTicket.objects.filter(user=user, ticket_opportunity=ticket_opp))
#         if available_tickets:
#             available_ticket = available_tickets[0]
#             available_ticket.status == 1
#         else:
#             available_ticket = AvailableTicket(
#                 ticket_opportunity=ticket_opp,
#                 user=user,
#                 status=1
#             )
#         AvailableTicket.save(available_ticket)
#         day_ago = (timezone.now() - datetime.timedelta(days=1))
#         logger.info("Giving away tickets!")
#         from actstream.models import target_stream
#         share_reward_history = list(user.target_actions.filter(verb='gave 20 share tickets to').order_by('-id'))
#         print "share reward history"
#         print share_reward_history
#         if share_reward_history:
#             share_reward_history = share_reward_history[0]
#             print "most recent share_reward_history"
#             print share_reward_history
#             print "share reward history timestamp"
#             print share_reward_history.timestamp
#             print day_ago
#             if share_reward_history.timestamp < day_ago:
#                 logger.info('Awarding: {}'.format(user))
#                 rm.give_tickets(user=user, amount=ticket_opp.tickets)
#                 action.send(rm, verb='gave 20 share tickets to', target=user)
#             else:
#                 print "patience my friend"
#         else:
#             logger.info('Awarding: {}'.format(user))
#             rm.give_tickets(user=user, amount=ticket_opp.tickets)
#             action.send(rm, verb='gave 20 share tickets to', target=user)
#         RaffleMaster.save(rm)
#         User.save(user)
#         TicketOpportunity.save(ticket_opp)
#         logger.info("All done!")
#
#
# @periodic_task(run_every=timedelta(hours=24))
# def login_tickets():
#     print "starting login tickets"
#     logger.info("Resetting Login Tickets Status")
#     rm = RaffleMaster.objects.first()
#     users = list(User.objects.all())
#     ticket_opp, created = TicketOpportunity.objects.get_or_create(name="Login Tickets", tickets=100, full_description='Daily tickets just for the heck of it!', status=1)
#     for user in users:
#         available_tickets = list(AvailableTicket.objects.filter(user=user, ticket_opportunity=ticket_opp))
#         if available_tickets:
#             available_ticket = available_tickets[0]
#             available_ticket.status == 1
#         else:
#             available_ticket = AvailableTicket(
#                 ticket_opportunity=ticket_opp,
#                 user=user,
#                 status=1
#             )
#         AvailableTicket.save(available_ticket)
#         day_ago = (timezone.now() - datetime.timedelta(days=1))
#         logger.info("Giving away tickets!")
#         if user.last_activity > day_ago:
#             logger.info('Awarding: {}'.format(user))
#             rm.give_tickets(user=user, amount=ticket_opp.tickets)
#         RaffleMaster.save(rm)
#         User.save(user)
#         TicketOpportunity.save(ticket_opp)
#     logger.info("All done!")
#
#
# @app.task(name='rafflie.tasks.raffle_now')
# @transaction.atomic
# def raffle_now(raffle_id):
#     raffle_now_tasks = current_app.tasks['rafflie.tasks.raffle_now']
#     print "raffle tasks in the queue:"
#     print raffle_now_tasks
#     raffle = Raffle.objects.get(id=raffle_id)
#     winners = None
#     num_of_winners = 1
#     if raffle.num_of_winners is not None:
#         num_of_winners = raffle.num_of_winners
#     winners = raffle.draw_winners(num_of_winners=num_of_winners)
#     return winners
#
#
# @app.task
# def reset_login_tickets_status():
#     logger.info("Resetting Login Tickets Status")
#     rm = RaffleMaster.objects.first()
#     users = list(User.objects.all())
#     ticket_opp = TicketOpportunity.objects.get_or_create(name="Login Tickets", tickets=100, full_description='Daily tickets just for the heck of it!', status=1)
#     for user in users:
#         logger.info('Awarding: {}'.format(user))
#         available_tickets = list(AvailableTicket.objects.filter(user=user))
#         if available_tickets:
#             available_ticket = available_tickets[0]
#             available_ticket.status == 1
#         else:
#             available_ticket = AvailableTicket(
#                 ticket_opportunity=ticket_opp,
#                 user=user,
#                 status=1
#             )
#         AvailableTicket.save(available_ticket)
#         logger.info("Giving away tickets!")
#         rm.give_tickets(user=user, amount=ticket_opp.tickets)
#         RaffleMaster.save(rm)
#         User.save(user)
#         TicketOpportunity.save(ticket_opp)
#     logger.info("All done!")
#
#
#
#
#
#
#
# app.conf.timezone = 'UTC'
