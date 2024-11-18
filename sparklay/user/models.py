from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
from django.utils import timezone

class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', null=True, blank=True, verbose_name='аватарка пользователя')
    username = models.CharField(max_length=150, unique=True ,verbose_name='имя пользователя')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    is_email_verified = models.BooleanField(default=False, verbose_name='Почта подтверждена')
    
    class Meta:
        db_table = 'user'
    
    def __str__(self):
        return self.username


class ConfirmationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiration_time = timezone.now() - self.created_at
        return expiration_time.total_seconds() > 600

    def generate_code(self):
        self.code = ''.join(random.choices(string.digits, k=6))
        self.save()

    def __str__(self):
        return f"Code for {self.user.username}"