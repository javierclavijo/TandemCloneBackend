# Generated by Django 4.0.2 on 2022-04-28 11:18

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chats', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendchat',
            name='users',
            field=models.ManyToManyField(related_name='friend_chats', to=settings.AUTH_USER_MODEL),
        ),
    ]
