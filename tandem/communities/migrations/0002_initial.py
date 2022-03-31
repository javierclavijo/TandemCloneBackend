# Generated by Django 4.0.2 on 2022-03-31 07:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channelinterest',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interests', to='communities.channel'),
        ),
        migrations.AddConstraint(
            model_name='channel',
            constraint=models.CheckConstraint(check=models.Q(('end_proficiency_level__gte', django.db.models.expressions.F('start_proficiency_level'))), name='start_proficiency_level_gte_end_proficiency_level'),
        ),
        migrations.AddConstraint(
            model_name='membership',
            constraint=models.UniqueConstraint(fields=('user', 'channel'), name='unique_user_channel'),
        ),
        migrations.AddConstraint(
            model_name='channelinterest',
            constraint=models.UniqueConstraint(fields=('channel', 'interest'), name='unique_channel_interest'),
        ),
    ]
