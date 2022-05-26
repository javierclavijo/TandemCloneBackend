from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from common.models import ProficiencyLevel
from users.models import UserLanguage


class UserCrudTests(APITestCase):
    """Contains tests for the user CRUD endpoints."""

    client = APIClient()
    user_model = get_user_model()
    user = user_model.objects.get(username='test_user')

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
        params = {"search": "ipsum"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        users_ids = list(str(x) for x in self.user_model.objects.filter(
            Q(username__icontains=params['search']) | Q(description__icontains=params['search']))
                         .order_by('id')
                         .values_list('id', flat=True)[:10])
        response_ids = sorted([user['id'] for user in response.data['results']])
        self.assertEqual(response_ids, users_ids)

    def test_queryset_filter_by_native_language_has_correct_list(self):
        """
        Tests if the queryset returned by the user list endpoint contains the correct users when filtering by native
        language.
        """
        url = reverse('customuser-list')
        params = {"native_language": "DE", "size": 9999}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        users_ids = [str(x) for x in sorted(UserLanguage.objects.filter(language=params['native_language']).filter(
            level=ProficiencyLevel.NATIVE).values_list('user', flat=True))]
        response_ids = sorted([user['id'] for user in response.data['results']])
        self.assertEqual(response_ids, users_ids)

        # Additionally, check that the count of found objects is correct
        user_count = self.user_model.objects.filter(languages__language=params['native_language'],
                                                    languages__level=ProficiencyLevel.NATIVE).count()
        self.assertEqual(response.data['count'], user_count)

    def test_queryset_filter_by_foreign_language_and_levels_returns_correct_list(self):
        """
        Tests if the queryset returned by the user list endpoint contains the correct users when filtering by foreign
        language and levels.
        """
        url = reverse('customuser-list')
        params = {"learning_language": "IT", "levels": "BE"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        subquery = UserLanguage.objects.filter(language=params['learning_language']).filter(
            level=params['levels']).values_list('user', flat=True)
        users_ids = list(str(x) for x in self.user_model.objects.filter(pk__in=subquery)
                         .order_by('id')
                         .values_list('id', flat=True)[:10])

        response_ids = sorted([user['id'] for user in response.data['results']])
        self.assertEqual(response_ids, users_ids)

        # Additionally, check that the count of found objects is correct
        user_count = self.user_model.objects.filter(pk__in=subquery).count()
        self.assertEqual(response.data['count'], user_count)

    def test_user_detail_has_id_and_has_not_password(self):
        """
        Tests if the user detail endpoint returns the user's id and doesn't return the user's password.
        """
        url = reverse("customuser-detail", kwargs={'pk': self.user.id})
        response = self.client.get(url)
        user_object = self.user_model.objects.get(pk=self.user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(user_object.id
                                                  ))
        self.assertNotContains(response, 'password')

    def test_user_creation_succeeds_with_appropriate_data(self):
        """
        Tests whether user creation is successful with appropriate data.
        """
        new_user = {
            "username": "new_test_user",
            "password": "password",
            "email": "new_test_user@example.com",
            "nativeLanguages": ['IT']
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
        user_id = self.user.id
        url = reverse("customuser-detail", kwargs={'pk': user_id})
        response = self.client.patch(url, data=data, format='json')
        user_object = self.user_model.objects.get(pk=user_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_object.username, data['username'])
        self.assertEqual(user_object.email, data['email'])
        self.assertEqual(user_object.description, data['description'])
