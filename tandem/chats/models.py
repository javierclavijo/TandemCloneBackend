from django.conf import settings
from django.db import models

# Create your models here.
from django.db.models import F
from django.utils import timezone

from common.models import AvailableLanguage


class AbstractChatMessage(models.Model):
    content = models.TextField(
        max_length=2048
    )
    timestamp = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        abstract = True


class AbstractChatMessageTranslation(models.Model):
    # TODO: add original language field to translation and correction models
    # TODO: merge both models
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    translated_content = models.TextField(
        max_length=4096
    )

    class Meta:
        abstract = True


class AbstractChatMessageCorrection(models.Model):
    language = models.CharField(
        max_length=2,
        choices=AvailableLanguage.choices
    )
    corrected_content = models.TextField(
        max_length=4096
    )

    class Meta:
        abstract = True


class UserChatMessage(AbstractChatMessage):
    def save(self, *args, **kwargs):
        # Get or create a UserChat object
        try:
            chat = UserChat.objects.filter(users__id=self.author_id).get(users__id=self.recipient_id)
        except UserChat.DoesNotExist:
            chat = UserChat()
            chat.save()
            chat.users.add(self.author)
            chat.users.add(self.recipient)
            chat.save()
        self.chat = chat
        super().save(*args, **kwargs)

    chat = models.ForeignKey(
        to='UserChat',
        blank=False,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_user_chat_messages"
    )
    recipient = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_user_chat_messages'
    )

    class Meta:
        ordering = ['-timestamp']
        constraints = [
            models.CheckConstraint(
                name='author_not_equals_recipient',
                check=~models.Q(recipient=models.F('author'))
            )
        ]


class UserChat(models.Model):
    users = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        blank=False,
        related_name="chats"
    )


class UserChatMessageTranslation(AbstractChatMessageTranslation):
    message = models.ForeignKey(
        to='chats.UserChatMessage',
        on_delete=models.CASCADE,
        related_name='translations'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='user_unique_language_message',
                fields=['language', 'message']
            )
        ]


class UserChatMessageCorrection(models.Model):
    message = models.OneToOneField(
        to='chats.UserChatMessage',
        on_delete=models.CASCADE,
        related_name='correction',
    )


class ChannelChatMessage(AbstractChatMessage):
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_channel_chat_messages"
    )
    channel = models.ForeignKey(
        to='communities.Channel',
        on_delete=models.CASCADE,
        related_name='messages'
    )

    class Meta:
        ordering = ['-timestamp']


class ChannelChatMessageTranslation(AbstractChatMessageTranslation):
    message = models.ForeignKey(
        to='ChannelChatMessage',
        on_delete=models.CASCADE,
        related_name='translations'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='channel_unique_language_message',
                fields=['language', 'message']
            )
        ]


class ChannelChatMessageCorrection(AbstractChatMessageCorrection):
    message = models.OneToOneField(
        to='ChannelChatMessage',
        on_delete=models.CASCADE,
        related_name='correction',
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='author'
    )
