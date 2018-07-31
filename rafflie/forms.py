from django import forms

class EnterTickets(forms.Form):

    tickets = forms.CharField(label='Number of Tickets', max_length=100)

class EnterAddress(forms.Form):

    fullname = forms.CharField(label='Full Name', max_length=100)
    address = forms.CharField(label='Address', max_length=100)
    city = forms.CharField(label='City', max_length=100)
    state = forms.CharField(label='State', max_length=100)
    zipcode = forms.CharField(label='ZipCode', max_length=5)
