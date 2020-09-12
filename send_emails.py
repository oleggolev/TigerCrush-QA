# -------------------------------------------------------------------------------
# send_emails.py
# Author: Oleg Golev  (Princeton '22, CS BSE)
#         Gerald Huang (Princeton '22 ELE BSE) 
#
# Implements the emailing feature for when matches are found.
# -------------------------------------------------------------------------------

from app import mail, appl
from flask_mail import Message
from db_functions import getName
from string import Template
import os

# -------------------------------------------------------------------------------
# Helper function to send the emails within the application context.
# -------------------------------------------------------------------------------

def send_async_mail(msg):
    with appl.app_context():
        mail.send(msg)

# -------------------------------------------------------------------------------
# Sends an email to the two love birds when they match.
# -------------------------------------------------------------------------------

def send_match_email(netid1, netid2):

    print("Match emailing code running")

    # construct the email message body
    with open("match_template.txt", 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
        template = Template(template_file_content)
        message = template.substitute(PERSON1_NAME=getName(netid1).split(",")[0],
                                      PERSON2_NAME=getName(netid2).split(",")[0])

    # send the email
    msg = Message(subject="TigerCrush: And That's a Match!",
                  sender=os.environ.get('MAIL_DEFAULT_SENDER'),
                  recipients=[netid1 + "@princeton.edu", netid2 + "@princeton.edu"],
                  body=message)
    send_async_mail(msg)

    print("Email sent! A new match is made <3")

# -------------------------------------------------------------------------------
# Sends a new user email on first login
# -------------------------------------------------------------------------------

def send_welcome_email(netid):

    print("First login email code running")

    # construct the email message body
    with open("first_email.txt", 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
        template = Template(template_file_content)
        message = template.substitute(PERSON=getName(netid).split(",")[0])

    # send the email
    msg = Message(subject="TigerCrush: Welcome!",
                  sender=os.environ.get('MAIL_DEFAULT_SENDER'),
                  recipients=[netid + "@princeton.edu"],
                  body=message)
    send_async_mail(msg)

    print("Email sent! New user welcomed!")