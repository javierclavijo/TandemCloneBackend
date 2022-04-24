from django.contrib.auth import get_user_model
from rest_framework import serializers

from communities.models import Channel, ChannelRole, Membership


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
            'id',
            'url',
            'channel',
            'user',
            'role'
        ]