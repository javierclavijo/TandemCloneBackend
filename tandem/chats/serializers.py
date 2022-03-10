from django.contrib.auth import get_user_model
from rest_framework import serializers

from chats.models import UserChat, UserChatMessage, ChannelChatMessage


class UserChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChatMessage
        fields = [
            'author',
            'recipient',
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
            'users',
            'messages'
        ]


class ChannelChatMessageSerializer(serializers.ModelSerializer):
    author = serializers.HyperlinkedRelatedField(view_name='customuser-detail', read_only=True)

    class Meta:
        model = ChannelChatMessage
        fields = [
            'author',
            'content',
            'timestamp'
        ]
