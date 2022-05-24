from django.contrib import admin

# Register your models here.
from users.models import CustomUser, UserLanguage

admin.site.register(CustomUser)
admin.site.register(UserLanguage)
