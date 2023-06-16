from djoser import email
from djoser import utils

class ActivationEmail(email.ActivationEmail):
    template_name = 'emails/activation.html'
    def get_context_data(self):
        context = super().get_context_data()
        uid = context.get("uid")
        token= context.get("token")

        return context
    
class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'emails/password_reset.html'