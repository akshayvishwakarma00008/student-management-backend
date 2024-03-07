from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from account.renderers import UserRenderers
from .serializers import UserRegistrationSerializers,UserLoginSerializer, UserDetailsSerializer,UserChangePasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordRestSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationsview(APIView):
    renderer_classes = [UserRenderers]
    def post(self, request, format=None):
        serializer = UserRegistrationSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({'token':tokens,'message':'Registration Successful'},status=status.HTTP_201_CREATED)
        else:
            return Response({'message':'Registration Failure'},status=status.HTTP_400_BAD_REQUEST)
        
class UserLoginView(APIView):
    renderer_classes = [UserRenderers]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email,password=password)
            if user is not None:
                tokens = get_tokens_for_user(user)
                return Response({'token':tokens,'message':'Login Successful'},status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
        

class UserDetail(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class changeUserPasswordView(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data,context ={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'message':'Password Changed Sucessfully'},status=status.HTTP_200_OK)
        return Response({'message':"Error in Changing  Password"},status=status.HTTP_400_BAD_REQUEST)

class SendPasswordResetView(APIView):
    renderer_classes = [UserRenderers]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'message':'Password reset link has been sent please check your email'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class UserPasswordRestView(APIView):
    renderer_classes = [UserRenderers]
    def post (self, request, uid, token, format=None):
        serializers = UserPasswordRestSerializer(data=request.data,context={'uid':uid,'token':token})
        if serializers.is_valid(raise_exception=True):
            return Response({'message':'Password rest sucessful!!'},status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)