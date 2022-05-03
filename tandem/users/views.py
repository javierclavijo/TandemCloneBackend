from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions, status, parsers
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.reverse import reverse

from common.models import AvailableLanguage, ProficiencyLevel
from users.models import UserLanguage
from users.serializers import UserSerializer, UserLanguageSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allow users to be viewed or edited.
    """

    class Meta:
        model = get_user_model()

    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    # Disable PUT method, as it's not currently supported due to nested serializer fields
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # TODO: add a permission to check whether request.user matches the ViewSet's instance (or is admin)
        if self.action == 'create':
            permission_classes = []
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        """
        Creates a user and its associated language objects
        """
        data = request.data
        user_object = self.Meta.model.objects.create_user(
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

        serializer = self.get_serializer(user_object)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserLanguageViewSet(viewsets.ModelViewSet):
    """
    API endpoints that allow users to be viewed or edited.
    """

    class Meta:
        model = UserLanguage

    queryset = UserLanguage.objects.all()
    serializer_class = UserLanguageSerializer


class ObtainAuthTokenWithIdAndUrl(ObtainAuthToken):
    """
    Returns the user's auth token, plus their ID and detail URL.
    Source: https://stackoverflow.com/a/44457513
    """

    def post(self, request, *args, **kwargs):
        response = super(ObtainAuthTokenWithIdAndUrl, self).post(request, *args, *kwargs)
        token = Token.objects.get(key=response.data['token'])
        url = request.build_absolute_uri(reverse('customuser-detail', kwargs={'pk': str(token.user.id)}))
        return Response({'token': token.key, 'id': token.user_id, 'url': url})
