from django.contrib.auth import get_user_model, login, authenticate, logout
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer, extend_schema_view, \
    OpenApiParameter
from rest_framework import permissions, status, parsers, fields, mixins
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken, APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse

from common.models import ProficiencyLevel, AvailableLanguage
from users.filters import UserFilter
from users.models import UserLanguage
from users.serializers import UserSerializer, UserLanguageSerializer, UserPasswordUpdateSerializer


@extend_schema_view(
    retrieve=extend_schema(
        description="Returns the details of the specified user.",
    ),
    list=extend_schema(
        description="Returns a list of users.",
        parameters=[
            OpenApiParameter('levels', type=OpenApiTypes.STR, many=True,
                             description="Filters users by the level of their learning (i.e. non-native) languages. "),
        ]
    ),
    create=extend_schema(
        description="Creates a user."
    ),
    partial_update=extend_schema(
        description="Modifies the details of the specified user.",
    ),
    set_password=extend_schema(
        description="Sets the session's user's password",
        request=UserPasswordUpdateSerializer,
    )
)
class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Allows users to be viewed, created or edited.
    """

    class Meta:
        model = get_user_model()

    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    filterset_class = UserFilter

    # Disable PUT method, as it's not currently supported due to nested serializer fields
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        """
        Creates a user and its associated language objects
        """
        response = super(UserViewSet, self).create(request, *args, **kwargs)
        user_id = response.data['id']
        user_object = get_user_model().objects.get(id=user_id)

        try:
            native_languages = request.data["nativeLanguages"]
            if not isinstance(native_languages, list):
                raise ValueError('This field must be a list value.')

            if not len(native_languages):
                raise ValueError(
                    f'This field must include at least one of the following choices: {AvailableLanguage.values}.')

            for language in native_languages:
                if language not in AvailableLanguage.values:
                    raise ValueError(f"'{language}' is not a valid choice.")
                language_object = UserLanguage.objects.create(
                    user=user_object,
                    language=language,
                    level=ProficiencyLevel.NATIVE
                )
                language_object.save()

            serializer = self.get_serializer(user_object)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except KeyError:
            """Rollback the transaction if the native_languages attribute wasn't provided. """
            transaction.set_rollback(True)
            return Response({'nativeLanguages': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            """Rollback the transaction if native_languages doesn't have the correct format or any of the provided 
            languages is not a valid choice. """
            transaction.set_rollback(True)
            return Response({'nativeLanguages': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def set_password(self, request, *args, **kwargs):
        """Update the user's password. Uses a custom serializer class."""
        instance = self.get_object()
        try:
            password = request.data["password"]
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Filter the received request data to avoid setting unwanted data
        data = {"password": password}
        serializer = UserPasswordUpdateSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


@extend_schema_view(
    retrieve=extend_schema(
        description="Returns the details of the specified language object.",
    ),
    create=extend_schema(
        description="Creates a user language object."
    ),
    partial_update=extend_schema(
        description="Modifies the details of the specified language object.",
    ),
    destroy=extend_schema(
        description="Deletes the specified language object."
    )
)
class UserLanguageViewSet(mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """
    Allows user languages to be viewed, created or edited.
    """

    class Meta:
        model = UserLanguage

    queryset = UserLanguage.objects.all()
    serializer_class = UserLanguageSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head']


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


@extend_schema(
    responses={
        200: OpenApiResponse(response=inline_serializer(name="session_info_response", fields={
            "id": fields.UUIDField(allow_null=True),
            "url": fields.CharField(allow_blank=True),
        })),
    },
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def get_session_info(request):
    """
    Returns the user's ID and detail URL in case they're authenticated, or null if they're not. Always returns
     a CSRF token cookie, so that non-logged-in clients can fetch it and use it in login requests.
    """
    user = request.user
    if request.user.is_authenticated:
        user_id = str(user.id)
        url = request.build_absolute_uri(reverse('customuser-detail', kwargs={'pk': user_id}))
        return Response({'id': user_id, 'url': url}, status=status.HTTP_200_OK)
    else:
        return Response({'id': None, 'url': None}, status=status.HTTP_200_OK)
    # Sources:
    # - https://medium.com/swlh/django-rest-framework-and-spa-session-authentication-with-docker-and-nginx-aa64871f29cd
    # - https://briancaffey.github.io/2021/01/01/session-authentication-with-django-django-rest-framework-and-nuxt/
    # - https://stackoverflow.com/a/59120949


@extend_schema(
    request=inline_serializer(name="login_request", fields={
        "username": fields.CharField(),
        "password": fields.CharField(),
    }),
    responses={
        204: OpenApiResponse(description="Successful login.", response=None),
        401: OpenApiResponse(description="Invalid credentials.",
                             response=inline_serializer(name="login_response_unauthorized", fields={
                                 "non_field_errors": fields.ListField(child=fields.CharField())
                             })),
        403: OpenApiResponse(description="Required field not provided.",
                             response=inline_serializer(name="login_response_bad_request", fields={
                                 "username": fields.ListField(child=fields.CharField()),
                                 "password": fields.ListField(child=fields.CharField()),
                             })),
    })
class LoginView(APIView):
    """
    Attempts user login.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            username = request.data['username']
            password = request.data['password']
            user = authenticate(request=request, username=username, password=password)

            if user is None:
                return Response({"non_field_errors": ["Unable to log in with provided credentials."]},
                                status=status.HTTP_401_UNAUTHORIZED)

            login(request, user)
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        except KeyError as e:
            return Response({str(e.args[0]): ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
    #   Partial source: https://www.guguweb.com/2022/01/23/django-rest-framework-authentication-the-easy-way/


@extend_schema(
    responses={
        204: OpenApiResponse(description="Successful logout.", response=None),
    },
    request=None
)
class LogoutView(APIView):
    """
    Attempts user logout.
    """

    def post(self, request):
        logout(request)
        return Response(None, status.HTTP_204_NO_CONTENT)
