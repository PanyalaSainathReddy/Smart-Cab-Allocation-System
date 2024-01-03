import datetime
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.contrib.auth import authenticate, get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions, generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import (CookieTokenRefreshSerializer, RegisterSerializer, UserSerializer)
from .utils import (get_tokens_for_user, google_get_access_token,
                    google_get_user_info, delete_cookies, set_cookie_handler)

User = get_user_model()

class LoginView(APIView):
    def post(self, request, format=None):
        # Fetching the User details from the request body.
        data = request.data
        response = Response()
        username = data.get('username', None)
        password = data.get('password', None)

        # Checking if the User exists.
        if not User.objects.filter(username=username).exists():
            return Response({"Error": "User does not exist, please Signup!!"}, status=status.HTTP_404_NOT_FOUND)
        
        # Checking if the User has signed up using Google.
        if User.objects.get(username=username).is_google:
            return Response({"Error": "Please use Google Login"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticating the User.
        user = authenticate(username=username, password=password)

        # Checking if the User credentials are valid.
        if user is None:
            return Response({"Error": "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)
        
        # Checking if the User is active.
        if not user.is_active:
            return Response({"Error": "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
        
        # Generating the tokens for the User.
        data = get_tokens_for_user(user)

        # Setting Cookies for the User and status code.
        response = set_cookie_handler(response, 'refresh', data["refresh"], 15, 0, True)
        response = set_cookie_handler(response, 'access', data["access"], 0, 30, True)
        response = set_cookie_handler(response, 'LoggedIn', True, 15, 0, False)

        response.data = {"Success": "Login successfull", "data": data}
        return response


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        # Fetching the User details from the request body.
        data = request.data
        username = data.get('email', None)
        password = data.get('password', None)
        email = data.get('email', None)
        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)

        # Searching if the User already exists.
        if User.objects.filter(email=email).exists():
            return Response({"Error": "User already exists, try to sign-in!!"}, status=status.HTTP_409_CONFLICT)

        # Creating a User object and Setting the password, and saving it.
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()

        response = Response()

        # Authenticating the User after registering them
        user = authenticate(username=username, password=password)

        # Checking if the User exists
        if user is None:
            return Response({"Error": "Please Signup first!!"}, status=status.HTTP_404_NOT_FOUND)

        # Checking if the User is active
        if not user.is_active:
            return Response({"Error": "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)

        # Generating the tokens for the User.
        data = get_tokens_for_user(user)

        # Setting Cookies for the User and status code.
        response = set_cookie_handler(response, 'refresh', data["refresh"], 15, 0, True)
        response = set_cookie_handler(response, 'access', data["access"], 0, 30, True)
        response = set_cookie_handler(response, 'LoggedIn', True, 15, 0, False)

        # Sending the final response to the client.
        response.data = data
        response.status_code = status.HTTP_201_CREATED
        return response


class GoogleRegisterView(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = 'http://127.0.0.1:5500/login.html'

        if error or not code:
            params = urlencode({'Error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = 'http://127.0.0.1:8000/api/accounts/register/google/'

        try:
            access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
        except Exception:
            params = urlencode({'Error': "Failed to obtain access token from Google."})
            return redirect(f'{login_url}?{params}')

        try:
            user_data = google_get_user_info(access_token=access_token)
        except Exception:
            params = urlencode({'Error': "Failed to obtain user info from Google."})
            return redirect(f'{login_url}?{params}')

        try:
            user = User.objects.create(
                username=user_data['email'],
                email=user_data['email'],
                first_name=user_data.get('given_name', ''),
                last_name=user_data.get('family_name', ''),
                is_google=True,
            )
            print(user)
            user.set_password('google')
            user.save()
        except Exception:
            params = urlencode({'Error': "User already exists, try to sign-in!"})
            return redirect(f'{login_url}?{params}')

        response = Response(status=302)
        user = authenticate(username=user_data['email'], password='google')
        if user is None:
            return Response("Invalid username or password!!", status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            return Response("This account is not active!!", status=status.HTTP_404_NOT_FOUND)

        # Generating the tokens for the User, and setting cookies
        data = get_tokens_for_user(user)
        response = set_cookie_handler(response, 'refresh', data["refresh"], 15, 0, True)
        response = set_cookie_handler(response, 'access', data["access"], 0, 30, True)
        response = set_cookie_handler(response, 'LoggedIn', True, 15, 0, False)

        response['Location'] = 'http://127.0.0.1:5500/frontend/home/index.html'
        response.data = data
        return response
        

class GoogleLoginView(APIView):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = 'http://127.0.0.1:5500/login.html'

        if error or not code:
            params = urlencode({'Error': error})
            return redirect(f'{login_url}?{params}')

        redirect_uri = 'http://127.0.0.1:8000/api/accounts/login/google/'

        try:
            access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
        except Exception:
            params = urlencode({'Error': "Failed to obtain access token from Google."})
            return redirect(f'{login_url}?{params}')

        try:
            user_data = google_get_user_info(access_token=access_token)
        except Exception:
            params = urlencode({'Error': "Failed to obtain user info from Google."})
            return redirect(f'{login_url}?{params}')

        response = Response(status=302)

        if not User.objects.filter(email=user_data['email']).exists():
            params = urlencode({'Error': "Please Signup first!!"})
            return redirect(f'{login_url}?{params}')

        if not User.objects.get(email=user_data['email']).is_google:
            params = urlencode({'Error': "You signed up using email & password!!"})
            return redirect(f'{login_url}?{params}')

        user = authenticate(username=user_data['email'], password='google')

        if user is None:
            params = urlencode({'Error': "Please Signup first!!"})
            return redirect(f'{login_url}?{params}')
        
        if not user.is_active:
            params = urlencode({'Error': "This account is not active!!"})
            return redirect(f'{login_url}?{params}')

        data = get_tokens_for_user(user)
        response = set_cookie_handler(response, 'refresh', data["refresh"], 15, 0, True)
        response = set_cookie_handler(response, 'access', data["access"], 0, 30, True)
        response = set_cookie_handler(response, 'LoggedIn', True, 15, 0, False)

        response['Location'] = 'http://127.0.0.1:5500/frontend/home/index.html'
        response.data = {"Success": "Login successfull", "data": data}
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            refreshToken = request.COOKIES.get('refresh')
            token = RefreshToken(refreshToken)
            token.blacklist()
            res = Response()
            
            # Deleting all the cookies for the User.
            response = delete_cookies(res)

            # Sending final response to the client.
            return response
        except Exception:
            raise exceptions.ParseError("Invalid token")


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if request.COOKIES.get("refresh"):
            response = set_cookie_handler(response, 'access', response.data["access"], 0, 30, True)

        return super().finalize_response(request, response, *args, **kwargs)


class UserDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
