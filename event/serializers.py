from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.text import slugify
from event.models import Event, BetaSubscriber
from accounts.signals import user_signed_up


class SubmitEventSerializer(serializers.ModelSerializer):
    create_account = serializers.BooleanField(required=False)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=15, required=False)

    class Meta:
        model = Event
        fields = [
            "event_image", "title", "start_date", "city",
            "when", "description", "venue", "event_source",
            "link", "create_account", "first_name",
            "last_name", "email", "phone"
        ]

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def _generate_unique_username(self, base_username):
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"
        return username

    def _create_account(self, data):
        base_username = slugify(data['email'].split('@')[0])
        username = self._generate_unique_username(base_username)
        user = User.objects.create_user(
            username=username,
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.set_unusable_password()
        user.save()
        return user

    def create(self, validated_data):
        create_account = validated_data.pop('create_account', False)
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email')
        phone = validated_data.pop('phone', '')

        event = Event(**validated_data)
        event.submitter_first_name = first_name
        event.submitter_last_name = last_name
        event.submitter_email = email
        event.submitter_phone = phone
        event.submitter_account_created = False

        if create_account:
            user = self._create_account({
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            })
            event.submitter = user
            event.submitter_account_created = True
            user_signed_up.send(sender=self.__class__, user=user, event=event)

        event.save()
        return event
