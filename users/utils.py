import datetime
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
import uuid

class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator

# def create_token(user):
#     return urlsafe_base64_encode(force_bytes(user.id)) + '.' + token_generator.make_token(user)


def forgot_password_mail(email, user):
    now = datetime.datetime.now()
    year = now.year
    month = now.strftime("%m")
    day = now.strftime("%d")
    hour = now.strftime("%H")
    minute = now.strftime("%M")
    # token=urlsafe_base64_encode(force_bytes(user.id)) + '.' + token_generator.make_token(user)
    token=f'{str(uuid.uuid4())}{year}{str(uuid.uuid4())}{month}{str(uuid.uuid4())}{day}{str(uuid.uuid4())}{hour}{str(uuid.uuid4())}{minute}'
    uidb64=urlsafe_base64_encode(force_bytes(user.pk))
    absurl = f'http://127.0.0.1/8000/users/change_password/{token}/{uidb64}/'
    subject='Link do zmiany hasła'
    message=f'Kliknij w link i zmień hasło {absurl}'
    email_from=settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True
