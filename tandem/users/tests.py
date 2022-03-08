from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase


class UserCrudTests(APITestCase):
    """Contains tests for the user CRUD endpoints."""

    client = APIClient()
    user_model = get_user_model()
    user = user_model.objects.get(username='admin')

    # Specify data fixtures to be loaded as initial data
    fixtures = ['test_data.json']

    @classmethod
    def setUpClass(cls):
        super(UserCrudTests, cls).setUpClass()
        cls.client.force_authenticate(user=cls.user)

    def setUp(self):
        super(UserCrudTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_user_list_has_correct_length(self):
        """
        Tests if the user list endpoint's response returns the appropriate status code and contains all users (has the correct length).
        """
        url = reverse('customuser-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], self.user_model.objects.count())

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

    def test_user_creation_successful(self):
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
            ],
            "interests": [
                0,
                1
            ]
        }
        url = reverse("customuser-list")
        response = self.client.post(url, data=new_user, format='json')
        user_object = self.user_model.objects.get(pk=response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], user_object.username)
