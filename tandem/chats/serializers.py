from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

from chats.models import UserChat, UserChatMessage, ChannelChatMessage


class ChatMessageAuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'url',
            'username'
        ]


class UserChatMessageSerializer(serializers.HyperlinkedModelSerializer):
    author = ChatMessageAuthorSerializer(read_only=True)

    class Meta:
        model = UserChatMessage
        fields = [
            'id',
            'url',
            'author',
            'chat',
            'content',
            'timestamp'
        ]


class UserChatSerializer(serializers.HyperlinkedModelSerializer):
    messages = serializers.SerializerMethodField(method_name='get_messages')

    def to_representation(self, instance):
        ret = super(UserChatSerializer, self).to_representation(instance)
        ret['messageUrl'] = self.context['request'].build_absolute_uri(
            str(reverse('userchatmessage-list')) + '?chat=' + str(instance.id))
        return ret

    def get_messages(self, instance):
        queryset = instance.messages.order_by('-timestamp')[:1]
        return UserChatMessageSerializer(queryset, many=True, read_only=True,
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
        model = UserChat
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
