# Generated by Django 4.0.2 on 2022-03-08 07:37

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, max_length=2000)),
                ('language', models.CharField(choices=[('EN', 'English'), ('ES', 'Spanish'), ('FR', 'French'), ('DE', 'German'), ('IT', 'Italian')], max_length=2)),
                ('start_proficiency_level', models.CharField(choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2'), ('N', 'Native')], max_length=2)),
                ('end_proficiency_level', models.CharField(choices=[('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2'), ('N', 'Native')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='ChannelChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=2048)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ChannelChatMessageCorrection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('EN', 'English'), ('ES', 'Spanish'), ('FR', 'French'), ('DE', 'German'), ('IT', 'Italian')], max_length=2)),
                ('corrected_content', models.TextField(max_length=4096)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChannelChatMessageTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('EN', 'English'), ('ES', 'Spanish'), ('FR', 'French'), ('DE', 'German'), ('IT', 'Italian')], max_length=2)),
                ('translated_content', models.TextField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='ChannelInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest', models.CharField(choices=[('Sports', 'Sports'), ('Music', 'Music'), ('Literature', 'Literature'), ('Cinema', 'Cinema'), ('Video games', 'Video Games')], max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('U', 'User'), ('M', 'Moderator'), ('A', 'Administrator')], default='U', max_length=1)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='channels.channel')),
            ],
        ),
    ]
