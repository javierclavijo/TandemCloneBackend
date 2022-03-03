from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from channels.models import Membership
from users.models import UserLanguage, UserInterest, UserChatMessage


class UserLanguageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        """Exclude id and user attributes from the object's serialization"""
        ret = super(UserLanguageSerializer, self).to_representation(instance)
        del ret['id']
        del ret['user']
        return ret

    class Meta:
        model = UserLanguage
        fields = [
            'id',
            'user',
            'language',
            'level'
        ]


class UserInterestSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        """Return the interest's display name as the instance's representation"""
        ret = super(UserInterestSerializer, self).to_representation(instance)
        return ret['interest_display']

    interest_display = serializers.CharField(source='get_interest_display')

    class Meta:
        model = UserInterest
        fields = [
            'interest',
            'interest_display'
        ]


class UserMembershipSerializer(serializers.ModelSerializer):
    """Membership serializer to use in user serializer. Similar to ChannelMembershipSerializer, but includes the
    channel's ID instead of the user's. """
    role = serializers.CharField(source='get_role_display')
    channel = serializers.HyperlinkedRelatedField(view_name="channel-detail", read_only=True)

    class Meta:
        model = Membership
        fields = [
            'channel',
            'role'
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User serializer class. Does not include messages and related models."""
    languages = UserLanguageSerializer(many=True)
    interests = UserInterestSerializer(many=True, required=False)
    memberships = UserMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'url',
            'username',
            'email',
            'description',
            'friends',
            'languages',
            'interests',
            'groups',
            'memberships'
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'url',
            'name'
        ]


class UserChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChatMessage
        fields = [
            'author',
            'recipient',
            'content',
            'timestamp'
        ]
