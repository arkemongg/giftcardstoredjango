from djoser import email
from djoser import utils
from django.conf import settings
domain_url = ''
if settings.DEBUG == True:
    domain_url = 'http://127.0.0.1:5500'
else:
    domain_url = 'https://giftcardstoreweb.vercel.app'
    

class ActivationEmail(email.ActivationEmail):
    template_name = 'emails/activation.html'
    def get_context_data(self):
        context = super().get_context_data()
        uid = context.get("uid")
        token= context.get("token")
        url = domain_url
        context["url"] = url
        print(domain_url)
        return context
    
class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'emails/password_reset.html'
    def get_context_data(self):
        context = super().get_context_data()
        url = domain_url
        context["url"] = url
        print(domain_url)
        return context

class PasswordChangedEmail(email.PasswordChangedConfirmationEmail):
    template_name = 'emails/password_changed.html'
    