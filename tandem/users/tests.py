from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase, APIRequestFactory, force_authenticate

from common.models import ProficiencyLevel
from users.models import UserLanguage
from users.serializers import UserSerializer
from users.views import UserViewSet


class UserCrudTests(APITestCase):
    """Contains tests for the user CRUD endpoints."""

    client = APIClient()
    user_model = get_user_model()
    user = user_model.objects.get(username='admin')

    # Specify data fixtures to be loaded as initial data
    fixtures = ['test_data.json']

    def setUp(self):
        super(UserCrudTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_user_list_has_correct_length(self):
        """
        Tests if the user list endpoint's response returns the appropriate status code and contains all users (has
        the correct length).
        """
        url = reverse('customuser-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.user_model.objects.count())

    def test_queryset_filter_by_username_has_correct_list(self):
        """
        Tests if the queryset returned by the user list endpoint contains the correct users when filtering by username.
        """
        url = reverse('customuser-list')
        params = {"username": "o"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        users_ids = list(self.user_model.objects.filter(username__icontains=params['username'])
                         .order_by('id')
                         .values_list('id', flat=True)[:10])
        response_ids = sorted([user['id'] for user in response.data['results']])
        self.assertEqual(response_ids, users_ids)

        # Additionally, check that the count of found objects is correct
        user_count = self.user_model.objects.filter(username__icontains=params['username']).count()
        self.assertEqual(response.data['count'], user_count)

    def test_queryset_filter_by_native_language_has_correct_list(self):
        """
        Tests if the queryset returned by the user list endpoint contains the correct users when filtering by native
        language.
        """
        url = reverse('customuser-list')
        params = {"nativeLanguage": "DE"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        users_ids = list(self.user_model.objects.filter(languages__language=params['nativeLanguage'],
                                                        languages__level=ProficiencyLevel.NATIVE)
                         .order_by('id')
                         .values_list('id', flat=True)[:10])
        response_ids = sorted([user['id'] for user in response.data['results']])
        self.assertEqual(response_ids, users_ids)

        # Additionally, check that the count of found objects is correct
        user_count = self.user_model.objects.filter(languages__language=params['nativeLanguage'],
                                                    languages__level=ProficiencyLevel.NATIVE).count()
        self.assertEqual(response.data['count'], user_count)

    def test_queryset_filter_by_foreign_language_and_levels_has_correct_list(self):
        """
        Tests if the queryset returned by the user list endpoint contains the correct users when filtering by foreign
        language and levels.
        """
        url = reverse('customuser-list')
        params = {"foreignLanguage": "IT", "levels": "B2,C1"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        levels_parts = params['levels'].split(',')
        subquery = UserLanguage.objects.filter(language=params['foreignLanguage'], level__in=levels_parts) \
            .exclude(level=ProficiencyLevel.NATIVE)
        users_ids = list(self.user_model.objects.filter(pk__in=subquery.values_list('user', flat=True))
                         .order_by('id')
                         .values_list('id', flat=True)[:10])

        response_ids = sorted([user['id'] for user in response.data['results']])
        self.assertEqual(response_ids, users_ids)

        # Additionally, check that the count of found objects is correct
        user_count = self.user_model.objects.filter(pk__in=subquery.values_list('user', flat=True)).count()
        self.assertEqual(response.data['count'], user_count)

    def test_user_detail_has_id_and_has_not_password(self):
        """
        Tests if the user detail endpoint returns the user's id and doesn't return the user's password.
        """
        user_id = 2
        url = reverse("customuser-detail", kwargs={'pk': 2})
        response = self.client.get(url)
        user_object = self.user_model.objects.get(pk=user_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user_object.id)
        self.assertNotContains(response, 'password')

    def test_user_creation_succeeds_with_appropriate_data(self):
        """
        Tests whether user creation is successful with appropriate data.
        """
        new_user = {
            "username": "test_user",
            "password": "password",
            "email": "test_user@example.com",
            "languages": [
                {
                    "language": "FR",
                    "level": "N"
                },
                {
                    "language": "ES",
                    "level": "B1"
                }
            ]
        }
        url = reverse("customuser-list")
        response = self.client.post(url, data=new_user, format='json')
        user_object = self.user_model.objects.get(pk=response.data['id'])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], user_object.username)

    def test_user_partial_update_succeeds_with_appropriate_data(self):
        """
        Tests whether user partial update succeeds with username, email and description.
        """
        data = {
            "username": "test_user_new_name",
            "email": "test_user_new_email@example.com",
            "description": 'new description'
        }
        user_id = 2
        url = reverse("customuser-detail", kwargs={'pk': user_id})
        response = self.client.patch(url, data=data, format='json')
        user_object = self.user_model.objects.get(pk=user_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_object.username, data['username'])
        self.assertEqual(user_object.email, data['email'])
        self.assertEqual(user_object.description, data['description'])

    def test_password_change_succeeds_with_appropriate_data(self):
        """
        Checks whether password change is successful.
        """
        data = {"password": "new_password"}
        user_id = 2
        url = reverse("customuser-set-password", kwargs={'pk': user_id})
        response = self.client.patch(url, data=data, format='json')
        user_object = self.user_model.objects.get(pk=user_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.client.login(username=user_object.username, password=data['password']))

    def test_password_change_fails_if_password_not_specified(self):
        """
        Checks whether password change fails and returns the appropriate error code if no 'password' key was
        specified in the request.
        """
        data = {"test": "new_password"}
        user_id = 2
        url = reverse("customuser-set-password", kwargs={'pk': user_id})
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_languages_succeeds_with_appropriate_data(self):
        """
        Checks whether language list update is successful. Coverage for this test depends on the user's extant
        language data and request data --ideally, the test's request should include at least a language the user
        already has with the same level, one that the user also has but with a different level, and another one that
        the user doesn't already have, as they are all treated differently in the view's code.
        """
        data = {
            "languages": [
                {
                    "language": "ES",
                    "level": "N"
                },
                {
                    "language": "IT",
                    "level": "B2"
                },
                {
                    "language": "FR",
                    "level": "A2"
                },
            ]
        }
        user_id = 2

        factory = APIRequestFactory()
        url = reverse("customuser-set-languages", kwargs={"pk": user_id})
        view = UserViewSet.as_view({'patch': 'set_languages'})
        request = factory.patch(url, data=data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request=request, pk=user_id)

        serializer = UserSerializer(
            instance=self.user_model.objects.get(pk=user_id),
            context={'request': request}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['languages'], serializer.data['languages'])

    def test_set_languages_fails_if_no_language_key(self):
        """
        Checks that language list update fails and returns the appropriate error code if no 'languages' key was sent
        in the request's body.
        """
        data = {}
        user_id = 2
        url = reverse("customuser-set-languages", kwargs={"pk": user_id})
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_languages_fails_if_language_name_not_specified(self):
        """
        Tests that language list update fails and returns the appropriate error code if the format of the 'languages'
        value is incorrect (has no 'language' key).
        """
        data = {"languages": [{
            "level": "A2"
        }]}
        user_id = 2
        url = reverse("customuser-set-languages", kwargs={"pk": user_id})
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_languages_fails_if_language_level_not_specified(self):
        """
        Tests that language list update fails and returns the appropriate error code if the format of the 'languages'
        value is incorrect (has no 'level' key).
        """
        data = {"languages": [{
            "language": "ES"
        }]}
        user_id = 2
        url = reverse("customuser-set-languages", kwargs={"pk": user_id})
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
