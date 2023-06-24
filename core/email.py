from djoser import email
from djoser import utils
from django.conf import settings
if settings.debug:
    domain_url = 'http://127.0.0.1:5500'
else:
    domain_url = 'https://giftcardstoreweb.vercel.app/'

class ActivationEmail(email.ActivationEmail):
    template_name = 'emails/activation.html'
    def get_context_data(self):
        context = super().get_context_data()
        uid = context.get("uid")
        token= context.get("token")
        url = domain_url
        return context
    
class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'emails/password_reset.html'

class PasswordChangedEmail(email.PasswordChangedConfirmationEmail):
    template_name = 'emails/password_changed.html'