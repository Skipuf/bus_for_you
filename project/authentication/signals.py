from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from database.models import Client, Carrier


@receiver(post_save, sender=Client)
def add_group_client(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='client')
        instance.user.groups.add(group)


@receiver(post_save, sender=Carrier)
def add_group_client(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='carrier')
        instance.user.groups.add(group)