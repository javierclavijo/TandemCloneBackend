from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from rest_framework.test import APIClient, APITestCase, APIRequestFactory, force_authenticate

from communities.models import Channel
from communities.serializers import ChannelSerializer
from communities.views import ChannelViewSet


class UserCrudTests(APITestCase):
    """Contains tests for the channel CRUD endpoints."""

    client = APIClient()
    model = Channel
    user = get_user_model().objects.get(username='admin')

    # Specify data fixtures to be loaded as initial data
    fixtures = ['test_data.json']

    def setUp(self):
        super(UserCrudTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_queryset_filter_by_name_has_correct_list(self):
        """
        Tests if the queryset returned by the channel list endpoint contains the correct items when filtering by name.
        """
        url = reverse('channel-list')
        params = {"name": "o"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        channel_ids = list(self.model.objects.filter(name__icontains=params['name'])
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = self.model.objects.filter(name__icontains=params['name']).count()
        self.assertEqual(response.data['count'], count)

    def test_queryset_filter_by_language_has_correct_list(self):
        """
        Tests if the queryset returned by the channel list endpoint contains the correct items when filtering by language.
        """
        url = reverse('channel-list')
        params = {"language": "FR"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        channel_ids = list(self.model.objects.filter(language=params['language'])
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = self.model.objects.filter(language=params['language']).count()
        self.assertEqual(response.data['count'], count)

    def test_queryset_filter_by_levels_has_correct_list(self):
        """
        Tests if the queryset returned by the channel list endpoint contains the correct items when filtering by levels.
        """
        url = reverse('channel-list')
        params = {"levels": "A1,B2"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        levels_parts = params['levels'].split(',')
        first_level = levels_parts.pop()
        level_queryset = Q(start_proficiency_level__lte=first_level, end_proficiency_level__gte=first_level)
        for level in levels_parts:
            level_queryset |= Q(start_proficiency_level__lte=level, end_proficiency_level__gte=level)

        channel_ids = list(self.model.objects.filter(level_queryset)
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = self.model.objects.filter(level_queryset).count()
        self.assertEqual(response.data['count'], count)

    def test_queryset_filter_by_interests_has_correct_list(self):
        """
        Tests if the queryset returned by the channel list endpoint contains the correct items when filtering by
        interests.
        """
        url = reverse('channel-list')
        params = {"interests": "Music,Cinema"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        interests = params['interests']
        channel_ids = list(self.model.objects.filter(interests__interest__in=interests.split(','))
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = self.model.objects.filter(interests__interest__in=interests.split(',')).count()
        self.assertEqual(response.data['count'], count)

    def test_set_interests_succeeds_with_appropriate_data(self):
        """
        Checks whether interest list update is successful.
        """
        data = {"interests": ["Sports", "Cinema", "Music"]}
        channel_id = 2

        factory = APIRequestFactory()
        url = reverse("channel-set-interests", kwargs={"pk": channel_id})
        view = ChannelViewSet.as_view({'patch': 'set_interests'})
        request = factory.patch(url, data=data, format="json")
        force_authenticate(request, user=self.user)
        response = view(request=request, pk=channel_id)

        serializer = ChannelSerializer(
            instance=self.model.objects.get(pk=channel_id),
            context={'request': request}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['interests'], serializer.data['interests'])

    def test_set_interests_fails_if_no_interests_are_sent(self):
        """
        Checks whether interest list update fails when no interests are sent in the request's body ('interests' key).
        """
        data = {"invalid_key": []}
        url = reverse("channel-set-interests", kwargs={"pk": 2})
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_interests_fails_if_invalid_interests_are_sent(self):
        """
        Checks whether interest list update fails when invalid interests are sent in the request's body.
        """
        data = {"interests": ["Sports", "a"]}
        url = reverse("channel-set-interests", kwargs={"pk": 2})
        response = self.client.patch(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
