from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
import uuid

from users.models import BlacklistToken

# class TokenGenerator(PasswordResetTokenGenerator):
#     pass


# token_generator = TokenGenerator

# def create_token(user):
#     return urlsafe_base64_encode(force_bytes(user.id)) + '.' + token_generator.make_token(user)

def create_token():
    now = datetime.now()
    year = now.year
    month = now.strftime("%m")
    day = now.strftime("%d")
    hour = now.strftime("%H")
    minute = now.strftime("%M")
    token=f'{str(uuid.uuid4())}{year}{str(uuid.uuid4())}{month}{str(uuid.uuid4())}{day}{str(uuid.uuid4())}{hour}{str(uuid.uuid4())}{minute}'
    return token

def blacklist_token(token):
    token_to_blacklist = BlacklistToken(
        token=token
    )
    token_to_blacklist.save()

def forgot_password_mail(email, user):
    # now = datetime.now()
    # year = now.year
    # month = now.strftime("%m")
    # day = now.strftime("%d")
    # hour = now.strftime("%H")
    # minute = now.strftime("%M")
    # token=f'{str(uuid.uuid4())}{year}{str(uuid.uuid4())}{month}{str(uuid.uuid4())}{day}{str(uuid.uuid4())}{hour}{str(uuid.uuid4())}{minute}'
    token = create_token()
    uidb64=urlsafe_base64_encode(force_bytes(user.pk))
    absurl = f'http://127.0.0.1/8000/users/change_password/{token}/{uidb64}/'
    subject='Link do zmiany hasła'
    message=f'Kliknij w link i zmień hasło {absurl}'
    email_from=settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True


def check_user_ip_mail(user):
    # blacklist_token(user.fp_token)
    token = create_token()
    uidb64=urlsafe_base64_encode(force_bytes(user.pk))
    block = f'http://127.0.0.1/8000/users/block_ip_address/{token}/{uidb64}/'
    accept = f'http://127.0.0.1/8000/users/accept_ip_address/{token}/{uidb64}/'
    subject='Weryfikacja'
    email_from=settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    message = f'Zalogowałeś się z innego urządzenia. \
               Jeśli to nie Ty to zablokuj to urządzenie klikając w link {block}. \
               Lub kontynuj: {accept}'
    send_mail(subject, message, email_from, recipient_list)