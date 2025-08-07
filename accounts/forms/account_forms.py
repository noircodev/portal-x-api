from django.db import transaction
from django.db.models import Q
from django import forms
from event.models import (SearchPhrase, Location)
from django.http import (HttpRequest)


class SearchKeywordForm(forms.Form):
    """
    Form for adding a new search phrase.
    """

    def __init__(self, request: HttpRequest, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user

    keyword = forms.CharField()

    def save(self):
        """
        Save the search phrase to the database.
        """
        keywords: str = self.cleaned_data['keyword']
        if keywords:
            locations = Location.objects.all()
            for word in keywords.split(','):
                if not SearchPhrase.objects.filter(query__iexact=word.strip()).exists():
                    # Create a new SearchPhrase object if it doesn't exist
                    # and associate it with the current user
                    new_keyword = SearchPhrase.objects.create(
                        query=word.strip().title(),
                        added_by=self.user
                    )
                    new_keyword.location.set(locations)
                    new_keyword.save()
        return keywords


class SearchKeywordForm(forms.Form):
    """
    Form for adding a new search phrase.
    """
    keyword = forms.CharField()

    def __init__(self, request: HttpRequest, *args, **kwargs):
        self.user = request.user
        super().__init__(*args, **kwargs)

    def save(self):
        """
        Save the search phrases to the database, skipping existing ones.
        """
        keywords_input = self.cleaned_data['keyword']
        if not keywords_input:
            return []

        # Normalize and split input
        words = {word.strip().title()
                 for word in keywords_input.split(',') if word.strip()}
        if not words:
            return []

        # Query existing phrases only once
        existing_queries = set(
            SearchPhrase.objects.filter(
                query__in=words).values_list('query', flat=True)
        )
        new_phrases = words - existing_queries

        # Fetch locations only if needed
        if new_phrases:
            locations = list(Location.objects.all())

        # Create new SearchPhrase objects
        for phrase in new_phrases:
            new_keyword = SearchPhrase.objects.create(
                query=phrase,
                added_by=self.user
            )
            new_keyword.location.set(locations)

        return list(words)


class SearchKeywordFormdd(forms.Form):
    """
    Form for adding new search phrases with optimized database operations.
    """
    keyword = forms.CharField(
        label='Search Phrases',
        help_text='Enter comma-separated search phrases.',
        widget=forms.TextInput(
            attrs={'placeholder': 'e.g., pizza, burgers, sushi'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        """Validate and preprocess keywords."""
        cleaned_data = super().clean()
        keywords = cleaned_data.get('keyword', '')

        # Split and clean keywords
        stripped_words = [word.strip()
                          for word in keywords.split(',') if word.strip()]
        if not stripped_words:
            self.add_error(
                'keyword', 'Please enter at least one valid search phrase.')
            return cleaned_data

        cleaned_data['stripped_words'] = stripped_words
        return cleaned_data

    def save(self):
        """
        Save search phrases using bulk operations for better performance.
        Returns original comma-separated input string.
        """
        stripped_words = self.cleaned_data.get('stripped_words', [])
        if not stripped_words:
            return ''

        # Get existing phrases in a single query
        existing_phrases = self._get_existing_phrases(stripped_words)
        existing_lower = {phrase.query.lower() for phrase in existing_phrases}

        # Filter out existing phrases and deduplicate
        new_words = self._filter_and_deduplicate_words(
            stripped_words, existing_lower)
        if not new_words:
            return ', '.join(stripped_words)

        # Bulk create new phrases and their relationships
        with transaction.atomic():
            created_phrases = self._bulk_create_phrases(new_words)
            self._bulk_create_location_relations(created_phrases)

        return ', '.join(stripped_words)

    def _get_existing_phrases(self, words):
        """Get existing phrases using case-insensitive match in a single query."""
        conditions = Q()
        for word in words:
            conditions |= Q(query__iexact=word)
        return SearchPhrase.objects.filter(conditions)

    def _filter_and_deduplicate_words(self, words, existing_lower):
        """Filter new words and deduplicate by title-case."""
        new_words = [word for word in words if word.lower()
                     not in existing_lower]
        seen_titles = set()
        deduped_words = []

        for word in new_words:
            title = word.title()
            if title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                deduped_words.append(word)
        return deduped_words

    def _bulk_create_phrases(self, words):
        """Create multiple SearchPhrase objects in a single query."""
        return SearchPhrase.objects.bulk_create([
            SearchPhrase(query=word.title(), added_by=self.user)
            for word in words
        ])

    def _bulk_create_location_relations(self, phrases):
        """Create m2m relationships with locations in bulk."""
        locations = list(Location.objects.all())
        if not locations:
            return

        through_model = SearchPhrase.location.through
        through_objs = [
            through_model(searchphrase=phrase, location=location)
            for phrase in phrases
            for location in locations
        ]
        through_model.objects.bulk_create(through_objs)


class UpdateSearchKeywordForm(forms.Form):
    """
    Form for adding new search phrases with optimized database operations.
    """
    keyword = forms.CharField()
    instance_id = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def update(self):
        """
        Update a single search phrase.
        """
        keyword = self.cleaned_data['keyword']
        instance_id = self.cleaned_data['instance_id']
        SearchPhrase.objects.filter(id=instance_id).update(query=keyword)
        return keyword

    def delete(self):
        """
        Delete a single search phrase.
        """
        instance_id = self.cleaned_data['instance_id']
        SearchPhrase.objects.filter(id=instance_id).delete()
