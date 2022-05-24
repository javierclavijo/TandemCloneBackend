from django.contrib import admin

# Register your models here.
from chats.models import FriendChat, ChannelChatMessage, FriendChatMessage

admin.site.register(FriendChatMessage)
admin.site.register(FriendChat)
admin.site.register(ChannelChatMessage)
