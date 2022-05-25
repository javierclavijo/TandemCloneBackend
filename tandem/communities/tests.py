from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from communities.models import Channel


class UserCrudTests(APITestCase):
    """Contains tests for the channel CRUD endpoints."""

    client = APIClient()
    model = Channel
    user = get_user_model().objects.get(username='test_user')

    # Specify data fixtures to be loaded as initial data
    fixtures = ['test_data.json']

    def setUp(self):
        super(UserCrudTests, self).setUp()
        self.client.force_authenticate(user=self.user)

    def test_queryset_filter_by_name_has_correct_list(self):
        """
        Tests if the queryset returned by the channel list endpoint contains the correct items when filtering by name
        or description.
        """
        url = reverse('channel-list')
        params = {"search": "wie"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        query = self.model.objects.filter(
            Q(name__icontains=params['search']) | Q(description__icontains=params['search']))
        channel_ids = list(str(x) for x in query
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = query.count()
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
        channel_ids = list(str(x) for x in self.model.objects.filter(language=params['language'])
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = self.model.objects.filter(language=params['language']).count()
        self.assertEqual(response.data['count'], count)

    def test_queryset_filter_by_level_has_correct_list(self):
        """
        Tests if the queryset returned by the channel list endpoint contains the correct items when filtering by level.
        """
        url = reverse('channel-list')
        params = {"level": "IN"}
        response = self.client.get(url, data=params)

        channel_ids = list(str(x) for x in self.model.objects.filter(level=params['level'])
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = self.model.objects.filter(level=params['level']).count()
        self.assertEqual(response.data['count'], count)

    def test_channel_creation_creates_admin_membership(self):
        """
        Tests that an admin membership is created for a user when they create a channel.
        """
        url = reverse('channel-list')
        data = {
            'name': 'new channel',
            'language': 'DE',
            'level': 'BE'
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(1, len(response.data['memberships']))
        self.assertIn(str(self.user.id), response.data['memberships'][0]['user'])
        self.assertEqual('Administrator', response.data['memberships'][0]['role'])
