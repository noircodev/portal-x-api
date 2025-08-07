from event.views.api_views import (IndexAPIView, SearchResultAPIView, SubmitEventAPIView, BetaSubscriberAPIView,
                                   SearchSuggestionAPIView,



                                   )


index_view = IndexAPIView.as_view()
search_result_view = SearchResultAPIView.as_view()
submit_event_view = SubmitEventAPIView.as_view()
join_beta_view = BetaSubscriberAPIView.as_view()
search_suggestion_view = SearchSuggestionAPIView.as_view()
