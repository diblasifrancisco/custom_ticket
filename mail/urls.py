from django.conf.urls import url
from django.views.generic import TemplateView
from .views import (
    get_data,
    send_mail_with_ticket_pdf,
    generate_pdf_ticket,
    email_preview_pdf,
    GetEmailTest,
)

urlpatterns = [
    url(
        r'^mail/',
        get_data,
        name='mail'),
    url(
        r'^generate_pdf_ticket/$',
        generate_pdf_ticket,
        name='generate_pdf'
    ),
    url(
        r'^email_preview_pdf/$',
        email_preview_pdf,
        name='email_preview'
    ),
    url(
        r'^sent-mail-success/$',
        TemplateView.as_view(
            template_name='mail/successfully_mail.html'),
        name='successfully_mail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/form_send_mail$',
        GetEmailTest.as_view(),
        name='form_send_mail'
    ),
]
