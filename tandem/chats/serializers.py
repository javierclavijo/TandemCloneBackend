from django.contrib.auth import get_user_model
from rest_framework import serializers

from chats.models import UserChat, UserChatMessage, ChannelChatMessage
from communities.models import Channel


class ChatMessageAuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'url',
            'username'
        ]


class UserChatMessageSerializer(serializers.ModelSerializer):
    author = ChatMessageAuthorSerializer(read_only=True)

    class Meta:
        model = UserChatMessage
        fields = [
            'id',
            'url',
            'author',
            'content',
            'timestamp'
        ]


class UserChatSerializer(serializers.ModelSerializer):
    users = serializers.HyperlinkedRelatedField(
        view_name='customuser-detail',
        queryset=get_user_model().objects.all(),
        many=True
    )
    messages = UserChatMessageSerializer(many=True)

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
            'content',
            'timestamp'
        ]


class ChannelChatSerializer(serializers.ModelSerializer):
    messages = ChannelChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Channel
        fields = [
            'id',
            'url',
            'name',
            'messages'
        ]
