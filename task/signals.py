from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from event.models import (Location, SearchPhrase)


@receiver(post_save, sender=Location)
def update_search_phrase(sender, instance, created, **kwargs):
    if created:
        search_prases = SearchPhrase.objects.filter(active=True)
        for search_phrase in search_prases:
            search_phrase.location.add(instance)
            search_phrase.save()
