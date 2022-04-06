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
    def to_representation(self, instance):
        """Add the name of the user who is not the request's user to the chat's representation. Additionally,
        add a chat type attribute to allow the application to determine the chat's type. """
        ret = super(UserChatSerializer, self).to_representation(instance)
        ret['name'] = instance.users.exclude(pk=self.context['request'].user.pk).get().username
        ret['chat_type'] = 'user'
        return ret

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


class UserChatListSerializer(UserChatSerializer):
    """Serializer class for the user chat list view. Displays only the latest message sent to the chat."""
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
            'content',
            'timestamp'
        ]


class ChannelChatSerializer(serializers.HyperlinkedModelSerializer):
    def to_representation(self, instance):
        """Add a chat type attribute to allow the application to determine the chat's type."""
        ret = super(ChannelChatSerializer, self).to_representation(instance)
        ret['chat_type'] = 'channel'
        return ret

    messages = ChannelChatMessageSerializer(many=True, read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='channelchat-detail')

    class Meta:
        model = Channel
        fields = [
            'id',
            'url',
            'name',
            'messages'
        ]


class ChannelChatListSerializer(ChannelChatSerializer):
    """Serializer class for the channel chat list view. Displays only the latest message sent to the chat."""
    messages = serializers.SerializerMethodField(method_name='get_messages')

    def get_messages(self, instance):
        queryset = instance.messages.order_by('-timestamp')[:1]
        return ChannelChatMessageSerializer(queryset, many=True, read_only=True,
                                            context={'request': self.context['request']}).data

    class Meta:
        model = Channel
        fields = [
            'id',
            'url',
            'name',
            'messages'
        ]