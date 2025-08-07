from django.urls import path
from accounts.views import *

account_urls = [

    # account urls

    path('', index_view, name='account_home'),
    path('add-search-keywords/', add_search_keywords_view,
         name='account_add_search_keywords'),

    path('events/', event_list_view,
         name='account_event_list'),

    path('search-keywords/', search_keyword_view,
         name='account_search_keywords'),


    path('page-protected/', page_protected_view, name='account_page_protected'),
    path('zipcode/', zip_code_view, name='account_zip_code'),
    path('beta-subscriber/', beta_subscriber_view,
         name='account_beta_subscriber'),
    path('add-event/', add_event_view, name='account_add_event'),
    path('update-event/<int:pk>/', add_event_view, name='account_update_event'),







]
