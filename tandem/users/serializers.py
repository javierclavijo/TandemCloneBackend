from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from users.models import UserLanguage, UserInterest


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
    interest_display = serializers.CharField(source='get_interest_display')

    class Meta:
        model = UserInterest
        fields = [
            'interest',
            'interest_display'
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    languages = UserLanguageSerializer(many=True)
    interests = UserInterestSerializer(many=True)

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
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'url',
            'name'
        ]
