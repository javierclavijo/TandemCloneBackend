from django.contrib import admin

from communities.models import Membership, Channel

admin.site.register(Channel)
admin.site.register(Membership)
