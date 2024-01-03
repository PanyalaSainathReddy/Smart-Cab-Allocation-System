import datetime
from typing import Any, Dict
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def google_get_access_token(*, code: str, redirect_uri: str) -> str:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

    if not response.ok:
        raise ValidationError('Failed to obtain access token from Google.')

    access_token = response.json()['access_token']

    return access_token


def google_get_user_info(*, access_token: str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Failed to obtain user info from Google.')

    return response.json()


def delete_cookies(response):
    cookies_to_delete = ['access', 'refresh', 'LoggedIn']

    for cookie in cookies_to_delete:
        response.delete_cookie(cookie, domain="127.0.0.1")

    return response


def expiry_time(days, minutes):
    return datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=days, minutes=minutes), "%a, %d-%b-%Y %H:%M:%S GMT")


def set_cookie_handler(response, key, value, days, minutes, httponly):
    response.set_cookie(
        key=key,
        value=value,
        expires=expiry_time(days, minutes),
        secure=True,
        domain="127.0.0.1",
        httponly=httponly,
        samesite='Lax'
    )

    return response
