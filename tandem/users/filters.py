from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters import rest_framework as filters

from common.models import ProficiencyLevel, AvailableLanguage

user_model = get_user_model()


class UserFilter(filters.FilterSet):
    """
    Filter class for UserViewSet. Accepts a 'search' parameter that includes all users with a username or description
    which contains the search term.
    """
    search = filters.CharFilter(method='get_search')
    native_language = filters.MultipleChoiceFilter(
        field_name='languages__level',
        choices=AvailableLanguage.choices,
        method='get_native_language'
    )

    def get_search(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) | Q(description__icontains=value)
        )

    def get_native_language(self, queryset, name, values):
        return queryset.filter(
            languages__language__in=values,
            languages__level=ProficiencyLevel.NATIVE
        )

    class Meta:
        model = user_model
        fields = ('search', 'native_language')
