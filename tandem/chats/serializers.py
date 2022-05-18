from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

from chats.models import FriendChat, FriendChatMessage, ChannelChatMessage


class ChatMessageAuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'url',
            'username'
        ]


class FriendChatMessageSerializer(serializers.HyperlinkedModelSerializer):
    author = ChatMessageAuthorSerializer(read_only=True)

    class Meta:
        model = FriendChatMessage
        fields = [
            'id',
            'url',
            'author',
            'chat',
            'content',
            'timestamp'
        ]


class FriendChatSerializer(serializers.HyperlinkedModelSerializer):
    messages = serializers.SerializerMethodField(method_name='get_messages')

    def to_representation(self, instance):
        """ Add the chat's message list URL to the chat's representation."""
        ret = super(FriendChatSerializer, self).to_representation(instance)
        ret['messageUrl'] = self.context['request'].build_absolute_uri(
            str(reverse('friendchatmessage-list')) + '?chat=' + str(instance.id))
        return ret

    @extend_schema_field(FriendChatMessageSerializer(many=True))
    def get_messages(self, instance):
        # If the user is admin or a member of the chat, get only the chat's latest message. Else, return an empty
        # queryset.
        user = self.context['request'].user
        if user.is_staff or user in instance.users.all():
            queryset = instance.messages.order_by('-timestamp')[:1]
        else:
            queryset = instance.messages.none()
        return FriendChatMessageSerializer(queryset, many=True, read_only=True,
                                           context={'request': self.context['request']}).data

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        Source: https://stackoverflow.com/a/50633184
        """

        class NestedUserSerializer(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = get_user_model()
                depth = nested_depth - 1
                fields = ['id', 'url', 'username', 'image']

        if field_name == 'users':
            field_class = NestedUserSerializer

        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs

    class Meta:
        model = FriendChat
        fields = [
            'id',
            'url',
            'users',
            'messages'
        ]
        depth = 1


class ChannelChatMessageSerializer(serializers.HyperlinkedModelSerializer):
    author = ChatMessageAuthorSerializer(read_only=True)

    class Meta:
        model = ChannelChatMessage
        fields = [
            'id',
            'url',
            'author',
            'channel',
            'content',
            'timestamp'
        ]
