from django.contrib.auth import get_user_model
from rest_framework import serializers

from channels.models import Channel, Membership, ChannelInterest, ChannelRole


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


class ChannelMembershipSerializer(MembershipSerializer):
    """
    Membership serializer to use in channel serializer, for representational purposes. Excludes channel field from
    representation.
    """
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
        Return the interest's display name as the instance's representation.
        """
        ret = super(ChannelInterestSerializer, self).to_representation(instance)
        return ret['display_name']

    display_name = serializers.CharField(source='get_interest_display', read_only=True)

    class Meta:
        model = ChannelInterest
        fields = [
            'channel',
            'interest',
            'display_name'
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
