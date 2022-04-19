from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from communities.models import Channel


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
        params = {"levels": "NA,BE"}
        response = self.client.get(url, data=params)

        # Compare sorted lists of IDs
        # The endpoint returns paginated data, so we must specify a limit to the queryset
        levels_parts = params['levels'].split(',')
        first_level = levels_parts.pop()

        channel_ids = list(self.model.objects.filter(level__in=levels_parts)
                           .order_by('id')
                           .values_list('id', flat=True)[:10])
        response_ids = sorted([channel['id'] for channel in response.data['results']])
        self.assertEqual(response_ids, channel_ids)

        # Additionally, check that the count of found objects is correct
        count = self.model.objects.filter(level__in=levels_parts).count()
        self.assertEqual(response.data['count'], count)
