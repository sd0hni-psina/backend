from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.contrib.auth.password_validation import validate_password

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer dlya registracii polzovatelya"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')

    def validate(self,attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password didnt match, please try again."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer dlya vhoda polzovatelya"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("User not found.")
            if not user.is_active:
                raise serializers.ValidationError("User is deactivated.")
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")
    
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer dlya profilya polzovatelya"""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name','address', 'phone', 'username', 'created_at', 'updated_at')

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer dlya obnovleniya dannykh polzovatelya"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'address', 'phone', 'company', )
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer dlya izmeneniya parolya polzovatelya"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "New password didn't match, please try again."
            })
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user