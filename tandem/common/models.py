from django.db import models
from django.utils.translation import gettext_lazy as _


class AvailableLanguage(models.TextChoices):
    ENGLISH = 'EN', _('English')
    SPANISH = 'ES', _('Spanish')
    FRENCH = 'FR', _('French')
    GERMAN = 'DE', _('German')
    ITALIAN = 'IT', _('Italian')


class ProficiencyLevel(models.TextChoices):
    BEGINNER = 'BE', _('Beginner')
    INTERMEDIATE = 'IN', _('Intermediate')
    ADVANCED = 'AD', _('Advanced')
    NATIVE = 'NA'
