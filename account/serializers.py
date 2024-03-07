from rest_framework import serializers
from account.models import User
from django.utils.encoding import smart_str, force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util

class UserRegistrationSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','name','password']
        extra_kwargs ={
            'password':{'write_only':True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')
        email_exists = User.objects.filter(email=email)
        if email_exists:
            raise serializers.ValidationError("User with this Email already exists")
        else:
            return attrs

    def create(self,validate_data):
        return User.objects.create_user(**validate_data);


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email','created_at', 'updated_at']

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)

    class Meta:
        fields = ['password']

    def validate(self, attrs):
        password = attrs.get('password')
        user = self.context.get('user')
        if not password or len(password) <=0:
            raise serializers.ValidationError("Password cannot be empty!! try again.")
        user.set_password(password)
        user.save()
        return attrs
    
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields =['email']

    def validate(self, attrs):
        email = attrs.get('email')
        # check if the user is registered with this email id
        user = User.objects.filter(email=email).exists()
        if user:
            userData = User.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(userData.id))
            print("encoded id",user_id)

            token = PasswordResetTokenGenerator().make_token(userData)
            print("password reset token",token)

            link = 'https://localhost:3000/api/user/reset/'+user_id+'/'+token
            print("reset link",link)

            data ={
                'subject':"Reset password",
                'body':link,
                'to_email':userData.email

            }
            Util.send_email(data)

            return attrs
        else:
            raise ValueError('You email Id doesnt exit in the system')
       
class UserPasswordRestSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)

    class Meta:
        fields = ['password']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if not password or len(password) <=0:
                raise serializers.ValidationError("Password cannot be empty!! try again.")
            
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("The Token is invalid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("The Token is invalid or Expired")
        