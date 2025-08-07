from django import forms
from event.models import Event
from django.http import HttpRequest
from django.forms import ValidationError
from django.utils.translation import gettext as _


class EventForm(forms.ModelForm):
    instance_id = forms.IntegerField(required=False)

    class Meta:
        model = Event
        fields = ['title', 'event_image', 'start_date', 'end_date', 'description', 'venue', 'link', 'city', 'featured', 'valid']

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user

    def save(self, commit=True):
        event = super().save(commit=False)
        if commit:
            event.save()
        return event

    def save(self, commit=True):
        """
        Save the form instance (for adding a new entry).
        """
        instance = super().save(commit=False)
        if commit:
            instance.submitter = self.user
            instance.event_source = "added_by_admin"
            instance.active = True
            instance.save()
            self._save_m2m()  # Save many-to-many relationships, if any
        return instance

    def update(self):
        """
        Update the instance identified by `instance_id`.
        Handles `ManyToManyField` updates and ensures the event banner image retains its default value if not updated.
        """
        instance_id = self.cleaned_data.get("instance_id")
        if not instance_id:
            raise ValidationError(_("Instance ID is required for updates."))

        instance = self.Meta.model.objects.filter(pk=instance_id).first()
        if not instance:
            raise ValidationError(_("No instance found with the provided ID."))

        # Separate ManyToManyField values from other fields
        many_to_many_data = {}
        for field, value in self.cleaned_data.items():
            if field == "instance_id":  # Skip `instance_id`
                continue

            field_obj = self.Meta.model._meta.get_field(field)

            if field == "event_image":  # Handle the event banner image separately
                if value:  # Only update the event banner image if a new value is provided
                    setattr(instance, field, value)
            elif field_obj.many_to_many:
                many_to_many_data[field] = value
            else:
                setattr(instance, field, value)

        # Save the instance first (ensures `id` is set)
        instance.save()

        # Now update the ManyToManyField relationships
        for field, value in many_to_many_data.items():
            getattr(instance, field).set(value)

        self.message = _(
            f"{self.Meta.model._meta.verbose_name} updated successfully.")
        return instance

    def delete(self):
        """
        Delete the instance identified by `instance_id`.
        """
        instance_id = self.cleaned_data.get("instance_id")
        if not instance_id:
            raise ValidationError(_("Instance ID is required for deletions."))

        instance = self.Meta.model.objects.filter(pk=instance_id).first()
        if not instance:
            raise ValidationError(_("No instance found with the provided ID."))

        instance.delete()
        return instance


class EventForm(forms.ModelForm):
    instance_id = forms.IntegerField(required=False)

    class Meta:
        model = Event
        fields = [
            'title', 'event_image', 'start_date', 'end_date',
            'description', 'venue', 'link', 'city', 'featured', 'valid'
        ]

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user
        self.message = None

    def clean_instance_id(self):
        instance_id = self.cleaned_data.get('instance_id')
        if instance_id:
            if not Event.objects.filter(pk=instance_id).exists():
                raise ValidationError(_("No event found with the provided ID."))
        return instance_id

    def save(self, commit=True):
        """
        Save the form instance (for adding a new entry).
        """
        instance = super().save(commit=False)
        instance.submitter = self.user
        instance.event_source = "added_by_admin"
        instance.active = True
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def update(self):
        """
        Update an existing instance using the provided form data.
        """
        if not self.is_valid():
            return None  # Form errors already populated

        instance_id = self.cleaned_data.get("instance_id")
        instance = Event.objects.filter(pk=instance_id).first()

        if not instance:
            self.add_error("instance_id", _("No event found with the provided ID."))
            return None

        many_to_many_data = {}

        for field, value in self.cleaned_data.items():
            if field == "instance_id":
                continue

            field_obj = self.Meta.model._meta.get_field(field)

            if field == "event_image":
                if value:
                    setattr(instance, field, value)
            elif field_obj.many_to_many:
                many_to_many_data[field] = value
            else:
                setattr(instance, field, value)

        instance.save()

        for field, value in many_to_many_data.items():
            getattr(instance, field).set(value)

        self.message = _(
            f"{self.Meta.model._meta.verbose_name.title()} updated successfully."
        )
        return instance

    def delete(self):
        """
        Delete an existing instance using the provided instance_id.
        """
        if not self.is_valid():
            return None

        instance_id = self.cleaned_data.get("instance_id")
        instance = Event.objects.filter(pk=instance_id).first()

        if not instance:
            self.add_error("instance_id", _("No event found with the provided ID."))
            return None

        instance.delete()
        self.message = _("Event deleted successfully.")
        return instance
