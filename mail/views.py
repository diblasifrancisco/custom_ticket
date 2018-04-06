# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import BadHeaderError, EmailMessage
from django.core.urlresolvers import reverse as r
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.views.generic import FormView
from .forms import FormSendEmailPreview
from events.models import CustomEmail, TicketType
from mail.utils import PDF
from django.core.mail import EmailMessage
from events.models import CustomEmail
from django.conf import settings
from eventbrite import Eventbrite
import requests
import json
import requests
from django.urls import reverse


def get_pdf_ticket(self):
    data = TicketType.data_to_dict(1)
    return PDF('tickets/template_default.html', [data]).render().getvalue()


def generate_pdf_ticket(request):
    ticket_pdf = get_pdf_ticket(request)
    return HttpResponse(ticket_pdf, content_type='application/pdf')


def get_pdf_body_email(request):
    data = CustomEmail.data_to_dict(1)
    return PDF('mail/body_mail.html', [data]).render().getvalue()


def email_preview_pdf(request):
    email_pdf = get_pdf_body_email(request)
    return HttpResponse(email_pdf, content_type='application/pdf')

# not use for testing - use do_send_email in mail/views.py


def send_mail_with_ticket_pdf(request):
    data = CustomEmail.data_to_dict(1)
    content = render_to_string('mail/body_mail.html', context=data)
    content = mark_safe(content)
    email = EmailMessage(
        'Test Send Ticket',
        content,
        'edacticket@gmail.com',
        ['usercticket@gmail.com']
    )
    email.content_subtype = 'html'
    pdf = get_pdf_ticket(request)
    email.attach('ticket', pdf, 'application/pdf')
    email.send()
    return HttpResponseRedirect(r('mails:successfully_mail'))


def get_venue(venue_id):
    # import ipdb; ipdb.set_trace()
    access_token = settings.SERVER_ACCESS_TOKEN
    eventbrite = Eventbrite(access_token)
    data_venue_json = eventbrite.get('/venues/' + str(venue_id))
    data_venue = json.loads(data_venue_json)
    venue = data_venue['address']['address_1']
    return venue


def get_data(request):
    print "sending email"
    print request.body
    access_token = settings.SERVER_ACCESS_TOKEN
    data = requests.get(
        json.loads(
            request.body
        )['api_url'] + '?token=' + access_token + '&expand=event,attendee'
    )
    user_first_name = data.json()['first_name'],
    user_last_name = data.json()['last_name'],
    list_attendee = data.json()['attendees']
    attendees = []
    for att in list_attendee:
        attendee = {
            'attendee_first_name': att['profile']['first_name'],
            'attendee_last_name': att['profile']['last_name'],
            'cost_gross': att['costs']['gross']['value'],
            # 'barcode': att['barcodes']['barcode'],
            'answers': att['answers'],
            'ticket_class': att['ticket_class_name']
        }
        attendees.append(dict(attendee))
    event_name_text = data.json()['event']['name']['html']
    from_email = settings.EMAIL_HOST_USER
    event_start = data.json()['event']['start']['utc']
    venue_id = data.json()['event']['venue_id']
    venue = get_venue(str(venue_id))
    emails = data.json()['email']
    order_id = data.json()['id']
    order_created = data.json()['created']
    order_status = data.json()['status']

    return do_send_email(
        attendees=attendees,
        event_name_text=event_name_text,
        user_order_first_name=user_first_name,
        user_order_lasst_name=user_last_name,
        event_start=event_start,
        order_id=order_id,
        order_created=order_created,
        order_status=order_status,
        event_venue_location=venue,
        from_email=from_email,
        emails=emails
    )


    # event_name_text = 'EVENTO LALA'
    # from_email = settings.EMAIL_HOST_USER
    # emails = ['usercticket@gmail.com']
    # return do_send_email(event_name_text=event_name_text, from_email=from_email, emails=emails)


def do_send_email(
    attendees=[],
    organizer_logo='',
    event_name_text='',
    event_start='',
    event_venue_location={},
    #   reserved seating
    user_order_email='',
    order_id='',
    order_created='',
    user_order_first_name='',
    user_order_last_name='',
    order_status='',
    # payment_datetime='',
    ticket_class='',
    from_email='',
    emails=[]
):

    # context data
    data = CustomEmail.data_to_dict(1)
    # body email
    message = render_to_string('mail/body_mail.html', context=data)
    # compose email
    email = EmailMessage(
        event_name_text,
        message,
        from_email,
        emails,
        reply_to=emails,
        headers={'Message-ID': 'foo'},
    )
    email.content_subtype = 'html'
    pdf = get_pdf_ticket('')

    # attach ticket
    email.attach('ticket', pdf, 'application/pdf')
    try:
        email.send()
        return HttpResponseRedirect(r('mails:successfully_mail'))
    except BadHeaderError:
        return HttpResponse('Invalid header found.')


class GetEmailTest(LoginRequiredMixin, FormView):
    form_class = FormSendEmailPreview
    template_name = 'mail/form_mail.html'

    def form_valid(self, form):
        print form.cleaned_data
        attendee_barcode = form.cleaned_data['attendee_barcode']
        attendee_first_name = form.cleaned_data['attendee_first_name']
        attendee_last_name = form.cleaned_data['attendee_last_name']
        organizer_message = form.cleaned_data['organizer_message']
        organizer_logo = form.cleaned_data['organizer_logo']
        attendee_cost_gross = form.cleaned_data['attendee_cost_gross']
        attendee_quantity = form.cleaned_data['attendee_quantity']
        attendee_question = form.cleaned_data['attendee_question']
        organizer_logo = form.cleaned_data['organizer_logo']
        order_status = form.cleaned_data['order_status']
        order_created = form.cleaned_data['order_created']
        ticket_class = form.cleaned_data['ticket_class']
        event_name_text = form.cleaned_data['event_name_text']
        event_image = form.cleaned_data['event_image']
        event_start = form.cleaned_data['event_start']
        event_venue_location = form.cleaned_data['event_venue_location']
        user_order_email = form.cleaned_data['user_order_email']
        user_order_first_name = form.cleaned_data['user_order_first_name']
        user_order_last_name = form.cleaned_data['user_order_last_name']
        from_email = form.cleaned_data['from_email']
        emails = [form.cleaned_data['emails']]
        attendees = []
        attendee = {
            'attendee_first_name': attendee_first_name,
            'attendee_last_name': attendee_last_name,
            'cost_gross': attendee_cost_gross,
            # 'barcode': att['barcodes']['barcode'],
            'answers': {},
            'ticket_class': ticket_class
        }

        attendees.append(dict(attendee))
        do_send_email(
            attendees=attendees,
            organizer_logo= organizer_logo,
            event_name_text= event_name_text,
            event_start= event_start,
            event_venue_location={ event_venue_location },
            #   reserved seating
            user_order_email=user_order_email,
            order_id= '1212',
            order_created=order_created,
            user_order_first_name=user_order_first_name,
            user_order_last_name=user_order_last_name,
            order_status=order_status,
            # payment_datetime='',
            ticket_class=ticket_class,
            from_email=from_email,
            emails= emails
        )
        # id customization
        # args=(self.kwargs['pk'],)
        return HttpResponseRedirect(reverse('mails:successfully_mail'))