from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from user.models import ConfirmationCode
import datetime

@receiver(post_save, sender=ConfirmationCode)
def check_code_expiration(sender, instance, **kwargs):
    expiration_time = instance.created_at + datetime.timedelta(minutes=10)
    if timezone.now() > expiration_time:
        instance.delete()   