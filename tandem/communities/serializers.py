from rest_framework import serializers

from common.serializers import MembershipSerializer
from communities.models import Channel, Membership, ChannelInterest
from users.serializers import UserSerializer


class ChannelMembershipSerializer(MembershipSerializer):
    """
    Membership serializer to use in channel serializer, for representational purposes. Excludes channel field from
    representation.
    """

    user = UserSerializer(read_only=True)

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
            'url',
            'id',
            'name',
            'description',
            'language',
            'start_proficiency_level',
            'end_proficiency_level',
            'memberships',
            'interests',
        ]
