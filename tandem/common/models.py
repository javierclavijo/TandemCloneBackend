from django.db import models
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
