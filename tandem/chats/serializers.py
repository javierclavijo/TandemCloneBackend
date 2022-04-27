from django.contrib.auth import get_user_model
from rest_framework import serializers

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


class UserChatSerializer(serializers.ModelSerializer):
    users = serializers.HyperlinkedRelatedField(
        view_name='customuser-detail',
        queryset=get_user_model().objects.all(),
        many=True
    )
    messages = serializers.SerializerMethodField(method_name='get_messages')

    def get_messages(self, instance):
        queryset = instance.messages.order_by('-timestamp')[:1]
        return UserChatMessageSerializer(queryset, many=True, read_only=True,
                                         context={'request': self.context['request']}).data

    class Meta:
        model = UserChat
        fields = [
            'id',
            'url',
            'users',
            'messages'
        ]


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
