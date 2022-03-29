from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from rest_framework import serializers

from communities.models import Membership
from communities.serializers import MembershipSerializer
from users.models import UserLanguage, UserInterest


class UserLanguageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        """
        Exclude id and user attributes from the object's serialization.
        """
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
        """
        Return the interest's display name as the instance's representation.
        """
        ret = super(UserInterestSerializer, self).to_representation(instance)
        return ret['display_name']

    display_name = serializers.CharField(source='get_interest_display', read_only=True)

    class Meta:
        model = UserInterest
        fields = [
            'user',
            'interest',
            'display_name'
        ]


class UserMembershipSerializer(MembershipSerializer):
    """
    Membership serializer to use in user serializer, for representational purposes. Excludes user field from
    representation.
    """

    class Meta:
        model = Membership
        fields = [
            'url',
            'channel',
            'role'
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    User serializer class. Does not include messages and other models, nor the user's password. Related fields are
    set to be read only to avoid unwanted updates, as they should be done through custom controllers (views).
    """
    languages = UserLanguageSerializer(many=True, read_only=True)
    interests = UserInterestSerializer(many=True, required=False, read_only=True)
    memberships = UserMembershipSerializer(many=True, read_only=True)
    email = serializers.EmailField(allow_blank=False, label='Email address', max_length=254, required=True)

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
            'memberships'
        ]


class UserPasswordUpdateSerializer(UserSerializer):
    """
    Serializer to update user's password.
    """
    def to_representation(self, instance):
        ret = super(UserPasswordUpdateSerializer, self).to_representation(instance)
        del ret['password']
        return ret

    class Meta:
        model = get_user_model()
        fields = ['id', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        try:
            validated_data['password'] = make_password(validated_data['password'])
        except KeyError:
            return serializers.ValidationError("Attribute 'password' was not sent.")
        return super().update(instance, validated_data)
