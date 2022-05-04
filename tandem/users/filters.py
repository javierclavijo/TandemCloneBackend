from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError

from common.models import ProficiencyLevel, AvailableLanguage
from users.models import UserLanguage

user_model = get_user_model()


class UserFilter(filters.FilterSet):
    """
    Filter class for UserViewSet. Accepts a 'search' parameter that includes all users with a username or description
    which contains the search term.
    """
    search = filters.CharFilter(method='get_search')
    native_language = filters.MultipleChoiceFilter(
        field_name='languages',
        choices=AvailableLanguage.choices,
        method='get_native_language'
    )
    learning_language = filters.MultipleChoiceFilter(
        field_name='languages',
        choices=AvailableLanguage.choices,
        method='get_learning_language'
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

    def get_learning_language(self, queryset, name, values):
        """ Filter users using a subquery which finds all UserLanguage objects where language matches the
        specified language and level is not Native ('N'). """

        # Filter UserLanguage objects by the provided languages, excluding those with a 'native' proficiency level
        subquery = UserLanguage.objects.filter(language__in=values).exclude(level=ProficiencyLevel.NATIVE)

        try:
            # If a proficiency level is specified, verify that it's a valid level and filter the UserLanguage subquery
            # by it.
            level = self.data['level']
            if level not in ProficiencyLevel.values:
                raise ValidationError({'level': [f'{level} is not a valid choice.']})

            subquery = subquery.filter(level=level)
        except KeyError:
            pass

        # Filter the main queryset to include only the users referenced in the subquery's entries.
        return queryset.filter(pk__in=subquery.values_list('user', flat=True))

    class Meta:
        model = user_model
        fields = ('search', 'native_language', 'learning_language')
