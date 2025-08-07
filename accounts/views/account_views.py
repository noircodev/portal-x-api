from accounts.views.base import *


class IndexView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {

        }
        return render(request, 'account/index.html', context)


class EventListView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        event = Event.objects.filter(
            start_date__gte=timezone.now().date()).distinct()
        event = paginate_queryset(request, event, 50)  # Paginate the events
        # Prepare the context with paginated events
        form = EventSearchForm(request, request.GET)
        if form.is_valid():
            PER_PAGE = 50
            event = paginate_queryset(request, form.filter_event, PER_PAGE)
        context = {
            'events': event,
            'form': form,
        }
        return render(request, 'account/event/event_list.html', context)


class SearchKeywordsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        keyword = SearchPhrase.objects.all()
        context = {
            "keywords": keyword,

        }
        return render(request, 'account/search/search_keyword.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'update_keyword':
            form = UpdateSearchKeywordForm(request, request.POST)
            if form.is_valid():
                form.update()
                messages.success(
                    request, "Search keywords updated successfully.")
                return redirect('account_search_keywords')
        elif action == 'delete_keyword':
            form = UpdateSearchKeywordForm(request, request.POST)
            if form.is_valid():
                form.delete()
                messages.success(
                    request, "Search keywords deleted successfully.")
                return redirect('account_search_keywords')

        get_error_messages(request, form.errors)
        return redirect(request.META.get('HTTP_REFERER', 'account_review'))


class AddEventFileUploadView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):

        context = {


        }
        return render(request, 'account/event/add_event_file_upload.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'pasted_csv':
            form = SearchKeywordForm(request, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Search keywords added successfully.")
                return redirect('account_search_keywords')

        get_error_messages(request, form.errors)
        messages.success(request, "File uploaded successfully.")
        return redirect(request.META.get('HTTP_REFERER', 'account_review'))


class ZipCodeView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        location = Location.objects.all()
        context = {
            'locations': location,
        }
        return render(request, 'account/search/zip_codes.html', context)


class BetaSubscriberView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        subscriber = BetaSubscriber.objects.all()
        context = {
            'subscribers': subscriber,
        }
        return render(request, 'account/users/beta_subscribers.html', context)


class PageProtectedView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {
        }
        return render(request, 'account/page_protected.html', context)


class AddEventView(LoginRequiredMixin, View):
    template_name = 'account/event/add_event.html'

    def get_context_data(self, request, instance=None):
        """
        Build and return the context data for the view.
        If an instance is provided, prefill the form with the instance data.
        """
        context = {
            'cities': City.objects.all(),
            'event': instance,
        }
        if instance:
            context['form'] = EventForm(request=request, instance=instance)
        else:
            context['form'] = EventForm(request=request, instance=None)
        return context

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests: Render the form with the context data.
        """
        event_id = kwargs.get('pk')  # Fetch event ID from URL kwargs
        instance = None
        if event_id:  # If ID exists, fetch the event instance for updating
            instance = get_object_or_404(Event, id=event_id)
        context = self.get_context_data(request=request, instance=instance)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: Validate the form and save/update the event data.
        """
        provider_id = kwargs.get('pk')  # Fetch event ID from URL kwargs
        instance = None
        if provider_id:
            instance = Event.objects.get(pk=provider_id)

        form = EventForm(request, request.POST, request.FILES, instance=instance)
        print(request.POST)
        print(form.is_valid())
        if form.is_valid():
            action = request.POST.get('action')
            if action == 'save_continue':
                form.save()
                messages.success(request, "Event created successfully.")
                return redirect("account_add_event")
            elif action == 'update_event':
                event = form.update()
                messages.success(request, "Event updated successfully.")
                return redirect('account_update_event', pk=event.id)
            elif action == 'delete_event':
                event = form.delete()
                messages.success(request, "Event deleted successfully.")
                return redirect('account_event_list')
            return redirect('account_event_list')

        # Form is invalid; rebuild context and add errors
        context = self.get_context_data(request, instance=instance)
        context['form'] = form
        get_error_messages(request, form.errors)
        return render(request, self.template_name, context)
