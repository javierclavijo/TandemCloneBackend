from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class AvailableLanguage(models.TextChoices):
    ENGLISH = 'EN', _('English')
    SPANISH = 'ES', _('Spanish')
    FRENCH = 'FR', _('French')
    GERMAN = 'DE', _('German')
    ITALIAN = 'IT', _('Italian')


class ProficiencyLevel(models.TextChoices):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'
    NATIVE = 'N'


class Interest(models.IntegerChoices):
    # TODO: change this enum (and related classes) to TextChoices. Don't forget to update it in the Postman collection
    SPORTS = 0, _('Sports')
    MUSIC = 1, _('Music')
    LITERATURE = 2, _('Literature')
    CINEMA = 3, _('Cinema')
    VIDEO_GAMES = 4, _('Video games')


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
