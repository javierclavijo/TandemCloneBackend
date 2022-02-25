from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import UserChatMessage
from users.serializers import UserSerializer, GroupSerializer, UserChatMessageSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(
        url_path=r'chat/(?P<other_user>[0-9]+)',
        url_name='chat',
        detail=True,
        methods=['get']
    )
    def chat(self, request, other_user, *args, **kwargs):
        """
        Fetches an user's chat with another user.
        """
        user = self.get_object()
        queryset = UserChatMessage.objects.filter(
            Q(author=user, recipient_id=other_user) |
            Q(author_id=other_user, recipient=user)
        )
        message_serializer = UserChatMessageSerializer(
            queryset,
            context={'request': self.request},
            many=True
        )
        return Response(message_serializer.data)

    class Meta:
        model = get_user_model()


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    class Meta:
        model = Group
