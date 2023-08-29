from django.core.mail import EmailMessage
import os

class EmailUtil:
  @staticmethod
  def send_email(data):
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=os.environ.get('EMAIL_FROM'),
      to=[data['to_email']]
    )
    email.send()

#from twilio.rest import Client

# class SmsUtil:
#     @staticmethod
#     def send_sms(data):
#         account_sid = 'your_account_sid'
#         auth_token = 'your_auth_token'
#         client = Client(account_sid, auth_token)

#         message = client.messages.create(
#             body=data['body'],
#             from_='your_twilio_phone_number',
#             to=data['to_phone_number']
#         )

#         return message.sid

# sen= SmsUtil()
# sen.send_sms('dskjgbfkjgf')