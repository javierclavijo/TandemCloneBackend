from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from rest_framework.validators import UniqueValidator

from common.serializers import MembershipSerializer
from communities.models import Membership, Channel
from users.models import UserLanguage


class UserLanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserLanguage
        fields = [
            'id',
            'url',
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

    def to_representation(self, instance):
        """ Delete the email field from the instance's representation. """
        ret = super(UserSerializer, self).to_representation(instance)
        del ret['email']
        return ret

    languages = UserLanguageSerializer(many=True, read_only=True)

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        Source: https://stackoverflow.com/a/50633184
        """

        class NestedFriendChatSerializer(serializers.HyperlinkedModelSerializer):
            def build_nested_field(self, field_name_2, relation_info_2, nested_depth_2):
                class NestedUserSerializer(serializers.HyperlinkedModelSerializer):
                    class Meta:
                        model = relation_info_2.related_model
                        depth = nested_depth_2 - 1
                        fields = ['id', 'url', 'username', 'description', 'image']

                if field_name_2 == 'users':
                    field_class_2 = NestedUserSerializer

                field_kwargs_2 = get_nested_relation_kwargs(relation_info_2)

                return field_class_2, field_kwargs_2

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = ['id', 'url', 'users']

        class NestedChannelSerializer(serializers.HyperlinkedModelSerializer):
            class Meta:
                model = Channel
                depth = nested_depth - 2
                fields = ['id', 'url', 'name', 'description', 'language', 'level', 'image']

        class NestedMembershipSerializer(serializers.HyperlinkedModelSerializer):
            channel = NestedChannelSerializer(read_only=True)

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = ['id', 'url', 'channel', 'role']

        if field_name == 'friend_chats':
            field_class = NestedFriendChatSerializer
        if field_name == 'memberships':
            field_class = NestedMembershipSerializer

        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs

    image = serializers.ImageField(required=False)
    email = serializers.EmailField(required=True, validators=[UniqueValidator(
        queryset=get_user_model().objects.all(),
        message="A user with that email already exists."
    )])

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'url',
            'username',
            'description',
            'friend_chats',
            'languages',
            'memberships',
            'image',
            'email'
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
