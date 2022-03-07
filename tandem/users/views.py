from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.models import AvailableLanguage, ProficiencyLevel
from users.models import UserChatMessage, UserLanguage, UserInterest
from users.serializers import UserSerializer, GroupSerializer, UserChatMessageSerializer, UserLanguageSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = []
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

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

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        """
        Creates an user and its associated language and interest objects
        """
        data = request.data
        user_object = get_user_model().objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            is_staff=False
        )
        user_object.save()

        for user_language in data["languages"]:
            UserLanguage.objects.create(
                user=user_object,
                language=dict(AvailableLanguage.choices)[user_language['language']],
                level=dict(ProficiencyLevel.choices)[user_language['level']]
            )

        for user_interest in data["interests"]:
            UserInterest.objects.create(
                user=user_object,
                interest=user_interest
            )

        serializer = self.get_serializer(user_object)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(
        detail=True,
        methods=['patch']
    )
    def set_username(self, request, *args, **kwargs):
        """Update the user's username attribute. Filters the received request data to avoid setting unwanted data."""
        # TODO: consider whether to avoid duplicate code. For now, it just works, so let's leave it like this.
        instance = self.get_object()
        try:
            username = request.data["username"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = {"username": username}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['patch']
    )
    def set_password(self, request, *args, **kwargs):
        """Update the user's password. Filters the received request data to avoid setting unwanted data."""
        instance = self.get_object()
        try:
            password = request.data["password"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = {"password": password}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['patch']
    )
    def set_description(self, request, *args, **kwargs):
        """Update the user's description. Filters the received request data to avoid setting unwanted data."""
        instance = self.get_object()
        try:
            description = request.data["description"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = {"description": description}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['patch']
    )
    def set_friends(self, request, *args, **kwargs):
        """Update the user's friend list. Filters the received request data to avoid setting unwanted data."""
        instance = self.get_object()
        try:
            friends = request.data["friends"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = {"friends": friends}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(
        detail=True,
        methods=['patch']
    )
    @transaction.atomic()
    def set_languages(self, request, *args, **kwargs):
        """Update the user's language list. Must receive a list of dictionaries with key-value pairs for language and
        level."""
        instance = self.get_object()
        try:
            new_languages = request.data["languages"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        for language in new_languages:
            try:
                language_name = language['language']
                language_level = language['level']
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            # First, find the object for the language if there's already one for this user. This way, we also avoid
            # integrity errors. If more than one object is sent for the same language, it will be set to the last
            # one, avoiding duplication.
            try:
                # If an object is found, update it with the level set in the request
                language_object = instance.languages.get(language=language_name)
                language_object.level = language_level
                serializer = UserLanguageSerializer(
                    instance=language_object,
                    data=language,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            except UserLanguage.DoesNotExist:
                # If no object is found, create and save a new one
                data = {
                    'user': instance.id,
                    'language': language_name,
                    'level': language_level
                }
                serializer = UserLanguageSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        # The user object is actually not modified at all. Instead, it's used to get the data for the response.
        serializer = self.get_serializer(instance=instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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
