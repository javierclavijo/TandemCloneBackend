from django.contrib.auth import get_user_model
from rest_framework import serializers

from communities.models import Channel
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


class ChannelChatSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super(ChannelChatSerializer, self).to_representation(instance)
        del ret['url']
        return ret

    messages = ChannelChatMessageSerializer(many=True)

    class Meta:
        model = Channel
        fields = [
            'url',
            'messages'
        ]
