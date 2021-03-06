from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework import status
from re import compile
from .models import LoginLog
# Create your views here.

# patterns for detect input type when login
mail_compiler = compile(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$')
username_compiler = compile(r'^\w+$')

class RegisterUserView(CreateAPIView):
    serializer_class = UserSerializer
    model = User

@api_view(['GET', 'POST'])
def login_view(request):
    input_text = request.data.get('input', '')
    password = request.data.get('password', '')

    if mail_compiler.match(input_text):
        user_kwarg = {'email': input_text}
    elif username_compiler.match(input_text):
        user_kwarg = {'username': input_text}
    else:
        return Response(data={'message': 'Istifadəçi Adı və ya Email düzgün yazılmayıb!'}, status=status.HTTP_400_BAD_REQUEST)

    # if user with obtained username or email is exists and that user's password is correct then login
    if (user:=User.objects.filter(**user_kwarg).first()) and user.check_password(password):
        token = Token.objects.get_or_create(user=user)[0].key
        data = {
            'username': user.username,
            'id': user.pk,
            'token': token
        }
        # save login informations
        LoginLog.objects.create(
            username=user.username,
            user_agent=request.META.get('HTTP_USER_AGENT'),
            ip_adress=request.META.get('REMOTE_ADDR'),
        )
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        return Response(data={'message': 'Giriş məlumatları düzgün qeyd edilməyib!'}, status=status.HTTP_400_BAD_REQUEST)

# delete token from database and logout request
@api_view(['POST'])
def logout_view(request):
    request.user.auth_token.delete()
    logout(request)
    return Response(status=status.HTTP_200_OK)