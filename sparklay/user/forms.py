from django import forms
from django.contrib.auth.forms import *
from django.contrib.auth import authenticate
from user.models import User
from django.core.exceptions import ValidationError

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Электронная почта')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if user is None:
                    raise forms.ValidationError("Неверный email или пароль.")
            except User.DoesNotExist:
                raise forms.ValidationError("Неверный email или пароль.")
            
            cleaned_data['user'] = user
        return cleaned_data
    



class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтвердите пароль")

    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        error_messages = {
            'email': {
                'invalid': 'Введите корректный адрес электронной почты.',
                'required': 'Электронная почта обязательна.',
                'unique': 'Этот email уже используется.',
            },
            'username': {
                'required': 'Имя пользователя обязательно.',
                'unique': 'Это имя пользователя уже занято.',
            },
            'password': {
                'invalid': 'Пароль должен содержать буквы и цифры.',
                'required': 'Пароль обязателен.',
                'min_length': 'Пароль должен быть не менее 8 символов.',
                'max_length': 'Пароль не должен превышать 128 символов.',
                'confirm_password': 'Пароли не совпадают.',
                
            }
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_email_verified = False 
        if commit:
            user.save()
        return user

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль", strip=False,),
    new_password2 = forms.CharField(widget=forms.PasswordInput,label="Подтвердите пароль", strip=False,),

    class Meta:
        fields = ['new_password1', 'new_password2']
        error_messages = {
            'new_password1': {
                'invalid': 'Пароль должен содержать буквы и цифры.',
                'required': 'Пароль обязателен.',
                'min_length': 'Пароль должен быть не менее 8 символов.',
                'max_length': 'Пароль не должен превышать 128 символов.',
                'confirm_password': 'Пароли не совпадают.',
            },
            'new_password2': {
                'invalid': 'Пароли не совпадают.',
                'required': 'Подтверждение пароля обязательно.',
            },
        }