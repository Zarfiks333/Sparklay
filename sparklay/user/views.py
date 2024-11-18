from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.conf import settings
from django.http import JsonResponse
from django.contrib import auth
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import *
from user.forms import *
from django.contrib import messages
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from user.models import *

temporary_tokens = {}

def loginOrSingIn(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main:mainView'))

    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']  
            email = form.cleaned_data['email']  

            if user.email != email:
                messages.error(request, 'Неверный логин или пароль.')
                return redirect('user:loginOrSingIn')

            if not user.is_email_verified:
                messages.error(request, 'Почта не подтверждена. Проверьте ваш email.')
                return redirect('user:loginOrSingIn')
            
            if not user.check_password(password):
                messages.error(request, 'Неверный логин или пароль.')
                return redirect('user:loginOrSingIn')
            
            confirmation_code = ConfirmationCode.objects.create(user=user)
            confirmation_code.generate_code()

            if not request.user.is_authenticated:
                request.session['user_session_id'] = confirmation_code.user.username

            send_mail(
                'Ваш код для входа в систему',
                f'Ваш код для входа: {confirmation_code.code}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )



            return redirect('user:verify_code')

    else:
        form = UserLoginForm()

    context = {
        'title': 'Sparklay',
        'form': form,
    }
    return render(request, 'systemlogin/login.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            token = get_random_string(32)
            temporary_tokens[token] = user  

            confirmation_link = request.build_absolute_uri(
                reverse('user:confirm_email', args=[token])
            )
            send_mail(
                'Подтверждение регистрации',
                f'Для подтверждения регистрации перейдите по ссылке: {confirmation_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'На вашу почту отправлено письмо для подтверждения.')
            return redirect('user:register')
    else:
        form = UserRegisterForm()
    context = {
        'title': 'Sparklay',
        'form': form,
    }
    return render(request, 'systemlogin/register.html', context)

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main:index'))

def confirm_email(request, token):
    user = temporary_tokens.pop(token, None)
    if user:
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Ваш email подтвержден! Теперь вы можете войти в систему.')
        return redirect('user:loginOrSingIn')
    else:
        messages.error(request, 'Неверная или устаревшая ссылка подтверждения.')
        return redirect('user:register')

def verify_code(request):
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        code = request.POST.get('code')

        if code:
            session_user_id = request.session.get('user_session_id')

            try:
                confirmation_code = ConfirmationCode.objects.get(code=code, user__username=session_user_id)

                if confirmation_code.is_expired():
                    messages.error(request, "Код истек. Пожалуйста, запросите новый.")
                else:
                    user = confirmation_code.user
                    login(request, user)

                    del request.session['user_session_id']

                    return redirect('main:index')

            except ConfirmationCode.DoesNotExist:
                messages.error(request, "Неверный код подтверждения.")

    return render(request, 'systemlogin/verify_code.html')

def get_valid_code(session_user_id):
    try:
        code_instance = ConfirmationCode.objects.get(user__username=session_user_id)
        if code_instance.is_expired():
            code_instance.delete()
            return None
        return code_instance
    except ConfirmationCode.DoesNotExist:
        return None
    
def password_reset(request):
    if request.user.is_authenticated:
        return redirect('main:index')
    
    if request.method == "POST" and "email" in request.POST:
        email = request.POST.get("email")
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            messages.error(request, "Пользователь с таким email не найден.")
            return redirect('user:password_reset')

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(str(user.pk).encode())

        reset_url = f"{get_current_site(request).domain}/password_reset/{uid}/{token}/"
        email_subject = "Сброс пароля"
        email_message = f"Перейдите по следующей ссылке для сброса пароля: {reset_url}"

        send_mail(email_subject, 
                  email_message, 
                  'noreply@example.com', 
                  [email])

        messages.success(request, "Инструкции по сбросу пароля отправлены на ваш email.")
        return redirect('user:password_reset') 
    
    return render(request, 'systemlogin/password_reset_form.html')

def password_reset_confirm(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('main:index')

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Ссылка для сброса пароля недействительна.")
        return redirect('user:password_reset')

    if request.method == "POST":
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ваш пароль успешно изменен. Теперь вы можете войти в свой аккаунт.")
            return redirect('user:loginOrSingIn')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomSetPasswordForm(user)

    return render(request, 'systemlogin/password_reset_confirm.html', {'form': form})