import os
import csv
import sys

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapp.settings'
application = get_wsgi_application()

from rafflie.models import Raffle, Product, Owner, User

with open('csv/02-11-2017-Raffle-Ingest-Final.csv', 'rb') as f:
    reader = csv.reader(f)
    headers = []
    raffles = []
    products = []
    owners = []
    users = []
    for i, row in enumerate(reader):
        if i == 0:
            headers = row
        else:
            raffle = {}
            product = {}
            owner = {}
            user = {}
            for x, value in enumerate(row):
                this_header = headers[x]
                split_header = this_header.split(':')
                model = split_header[0]
                field = split_header[1]
                if model == 'raffle':
                    raffle[field] = value
                if model == 'product':
                    product[field] = value
                if model == 'owner':
                    owner[field] = value
                if model == 'user':
                    user[field] = value
            raffles.append(raffle)
            products.append(product)
            owners.append(owner)
            users.append(user)

for i, raffle in enumerate(raffles):
    product = products[i]
    owner = owners[i]
    user = users[i]

    u = User.objects.update_or_create(email=user['email'], defaults=user)[0]

    owner['user'] = User.objects.get(id=u.id)
    o = Owner.objects.update_or_create(email=owner['email'], defaults=owner)[0]

    product['owner'] = Owner.objects.get(id=o.id)
    p = Product.objects.update_or_create(name=product['name'], owner=o, defaults=product)[0]

    raffle['product'] = Product.objects.get(id=p.id)
    raffle['owner'] = Owner.objects.get(id=o.id)
    r = Raffle.objects.update_or_create(owner=o, product=p, defaults=raffle)[0]

    User.save(u)
    Owner.save(o)
    Product.save(p)
    Raffle.save(r)
