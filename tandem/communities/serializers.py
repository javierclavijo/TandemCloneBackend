from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

from communities.models import Channel


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Channel serializer class.
    """

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        Source: https://stackoverflow.com/a/50633184
        """

        class NestedUserSerializer(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = get_user_model()
                depth = nested_depth - 1
                fields = ['id', 'url', 'username', 'description']

        class NestedMembershipSerializer(serializers.HyperlinkedModelSerializer):
            user = NestedUserSerializer(read_only=True)

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = ['id', 'url', 'user', 'role']

        if field_name == 'memberships':
            field_class = NestedMembershipSerializer

        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs

    image = serializers.ImageField(required=False)

    class Meta:
        model = Channel
        fields = [
            'url',
            'id',
            'name',
            'description',
            'language',
            'level',
            'memberships',
            'image',
        ]
        depth = 2
