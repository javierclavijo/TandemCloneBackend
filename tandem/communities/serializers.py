from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

from chats.serializers import ChannelChatMessageSerializer
from communities.models import Channel, Membership


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Channel serializer class.
    """

    def to_representation(self, instance):
        ret = super(ChannelSerializer, self).to_representation(instance)
        ret['messageUrl'] = self.context['request'].build_absolute_uri(
            str(reverse('channelchatmessage-list')) + '?channel=' + str(instance.id))
        return ret

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

    messages = serializers.SerializerMethodField(method_name='get_messages')
    image = serializers.ImageField(required=False)

    def get_messages(self, instance):
        # If the user is admin or a member of the channel, get only the latest message for the channel. Else, return an
        # empty queryset.
        user = self.context['request'].user
        if user.is_staff or Membership.objects.filter(user=user, channel=instance).exists():
            queryset = instance.messages.order_by('-timestamp')[:1]
        else:
            queryset = instance.messages.none()
        return ChannelChatMessageSerializer(queryset, many=True, read_only=True,
                                            context={'request': self.context['request']}).data

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
            'messages'
        ]
        depth = 2
