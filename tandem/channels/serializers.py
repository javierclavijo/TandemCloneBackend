from django.contrib.auth import get_user_model
from rest_framework import serializers

from channels.models import Channel, Membership, ChannelInterest, ChannelChatMessage, ChannelRole


class MembershipSerializer(serializers.ModelSerializer):
    """
    Serializer used in MembershipViewSet to create, update and delete subscriptions of users to channels.
    """

    def to_representation(self, instance):
        ret = super(MembershipSerializer, self).to_representation(instance)
        ret['role'] = instance.get_role_display()
        return ret

    channel = serializers.HyperlinkedRelatedField(
        view_name='channel-detail',
        queryset=Channel.objects.all()
    )
    user = serializers.HyperlinkedRelatedField(
        view_name="customuser-detail",
        queryset=get_user_model().objects.all()
    )
    role = serializers.ChoiceField(
        choices=ChannelRole.choices,
        default=ChannelRole.USER
    )

    class Meta:
        model = Membership
        fields = [
            'url',
            'channel',
            'user',
            'role'
        ]


class ChannelMembershipSerializer(serializers.ModelSerializer):
    """
    Membership serializer to use in channel serializer. Similar to UserMembershipSerializer, but includes the
    user's ID instead of the channel's. Also includes the Membership object's url to perform update and delete
    operations.
    """
    # TODO: perhaps, refactor this and UserMembershipSerializer to inherit from MemberSerializer (hiding fields as
    #  required)
    role = serializers.CharField(source='get_role_display')
    user = serializers.HyperlinkedRelatedField(view_name="customuser-detail", read_only=True)

    class Meta:
        model = Membership
        fields = [
            'url',
            'user',
            'role'
        ]


class ChannelInterestSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        """
        Return the interest's display name as the instance's representation
        """
        ret = super(ChannelInterestSerializer, self).to_representation(instance)
        return ret['interest_display']

    interest_display = serializers.CharField(source='get_interest_display')

    class Meta:
        model = ChannelInterest
        fields = [
            'interest',
            'interest_display'
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


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Channel serializer class.
    """
    memberships = ChannelMembershipSerializer(many=True, read_only=True)
    interests = ChannelInterestSerializer(many=True, read_only=True)

    class Meta:
        model = Channel
        fields = [
            'id',
            'name',
            'description',
            'language',
            'start_proficiency_level',
            'end_proficiency_level',
            'memberships',
            'interests',
        ]
