from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase, APIRequestFactory, force_authenticate

# TODO: additional user test cases:
# Update/change password/etc. can only be performed by the same user or by an admin
# Failure cases with incorrect data

from users.serializers import UserSerializer
from users.views import UserViewSet


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

    def test_user_partial_update_successful(self):
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

    def test_password_change_successful(self):
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

    def test_set_friends_successful(self):
        """
        Checks whether friend list update is successful.
        """
        friend_ids = [3, 5, 7, 13]
        data = {"friends": []}
        user_id = 2

        for friend_id in friend_ids:
            friend_url = reverse("customuser-detail", kwargs={"pk": friend_id})
            data['friends'].append(friend_url)

        # We need to use a request factory to pass the request to the serializer
        factory = APIRequestFactory()
        url = reverse("customuser-set-friends", kwargs={"pk": user_id})
        view = UserViewSet.as_view({'patch': 'set_friends'})
        request = factory.patch(url, data=data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request=request, pk=user_id)

        serializer = UserSerializer(
            instance=self.user_model.objects.get(pk=user_id),
            context={'request': request}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['friends'], serializer.data['friends'])

    def test_set_friends_fails_if_no_friends_are_sent(self):
        """
        Checks whether friend list update fails and returns the appropriate status code if no 'friends' key is
        included in the request.
        """
        data = {"invalid_key": []}
        url = reverse("customuser-set-friends", kwargs={"pk": 2})
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_languages_successful(self):
        """
        Checks whether language list update is successful.
        """
        data = {
            "languages": [
                {
                    "language": "EN",
                    "level": "N"
                },
                {
                    "language": "FR",
                    "level": "A2"
                },
                {
                    "language": "DE",
                    "level": "B1"
                }
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

    def test_set_interests_successful(self):
        """
        Checks whether interest list update is successful.
        """
        data = {"interests": ["Sports", "Cinema", "Music"]}
        user_id = 2

        factory = APIRequestFactory()
        url = reverse("customuser-set-interests", kwargs={"pk": user_id})
        view = UserViewSet.as_view({'patch': 'set_interests'})
        request = factory.patch(url, data=data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request=request, pk=user_id)

        serializer = UserSerializer(
            instance=self.user_model.objects.get(pk=user_id),
            context={'request': request}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['interests'], serializer.data['interests'])

    def test_set_interests_fails_if_no_interests_are_sent(self):
        """
        Checks whether interest list update fails when no interests are sent in the request's body ('interests') key.
        """
        data = {"invalid_key": []}
        user_id = 2
        url = reverse("customuser-set-interests", kwargs={"pk": user_id})
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_interests_fails_if_invalid_interests_are_sent(self):
        """
        Checks whether interest list update fails when invalid interests are sent in the request's body.
        """
        data = {"interests": ["Sports", "Smoking"]}
        user_id = 2
        url = reverse("customuser-set-interests", kwargs={"pk": user_id})
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
