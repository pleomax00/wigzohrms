__author__ = 'shamailtayyab'
from django.core.mail import EmailMessage

def wigzomail (to, subject, body):
    email = EmailMessage(subject, body, to=to)
    email.send()