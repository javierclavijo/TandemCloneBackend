from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

from common.serializers import MembershipSerializer
from communities.models import Membership, Channel
from users.models import UserLanguage


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


class UserMembershipSerializer(MembershipSerializer):
    """
    Membership serializer to use in user serializer, for representational purposes. Excludes user field from
    representation.
    """

    class Meta:
        model = Membership
        fields = [
            'id',
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

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        Source: https://stackoverflow.com/a/50633184
        """

        class NestedUserSerializer(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = ['id', 'url', 'username', 'description']

        class NestedChannelSerializer(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = Channel
                depth = nested_depth - 2
                fields = ['id', 'url', 'name', 'description', 'language', 'level']

        class NestedMembershipSerializer(serializers.HyperlinkedModelSerializer):
            channel = NestedChannelSerializer(read_only=True)

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = ['id', 'url', 'channel', 'role']

        field_class = NestedUserSerializer
        if field_name == 'friends':
            field_class = NestedUserSerializer
        if field_name == 'memberships':
            field_class = NestedMembershipSerializer

        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'url',
            'username',
            'description',
            'friends',
            'languages',
            'memberships'
        ]
        depth = 2


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
