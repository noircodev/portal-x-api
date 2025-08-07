from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from event.api.views import (active_event_list_view)


from event.views import (
    index_view,
    search_result_view,
    submit_event_view,
    join_beta_view,
    search_suggestion_view,

)

app_name = 'event'

urlpatterns = [
    # Mobile API URLs (Inactive for now)
    path('api/token/', obtain_auth_token, name='api_token'),
    path('active/', active_event_list_view, name='active_events'),
    # App API paths
    path('', index_view, name='home'),
    path('search/', search_result_view, name='search'),
    path('submit-event/', submit_event_view, name='submit_event'),
    path('beta/subscribe/', join_beta_view, name='join_beta'),
    path('search/suggestions/', search_suggestion_view, name='search_suggestions'),

]
