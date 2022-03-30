from channels.routing import URLRouter
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from communities.views import ChannelViewSet, MembershipViewSet
from chats.views import UserChatViewSet, ChannelChatViewSet, ChatListView
from users import views

"""tandem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'memberships', MembershipViewSet)
router.register(r'user_chats', UserChatViewSet)
router.register(r'channel_chats', ChannelChatViewSet, basename='channelchat')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token),
    path('chat-list/', ChatListView.as_view())
]
