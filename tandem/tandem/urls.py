from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from rest_framework import routers

from chats.views import FriendChatViewSet, FriendChatMessageViewSet, \
    ChannelChatMessageViewSet
from communities.views import ChannelViewSet, MembershipViewSet
from users import views
from users.views import LoginView, get_session_info, LogoutView, SetPassword

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
router.register(r'user_languages', views.UserLanguageViewSet)
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'memberships', MembershipViewSet)
router.register(r'friend_chats', FriendChatViewSet)
router.register(r'friend_chat_messages', FriendChatMessageViewSet)
router.register(r'channel_chat_messages', ChannelChatMessageViewSet)

urlpatterns = [
                  path('api/', include(router.urls)),
                  path('api/admin/', admin.site.urls),

                  # Auth views
                  path('api/login/', LoginView.as_view()),
                  path('api/logout/', LogoutView.as_view()),
                  path('api/session_info/', get_session_info),
                  path('api/set_password/', SetPassword.as_view()),

                  # OpenAPI Documentation
                  path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
                  path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
