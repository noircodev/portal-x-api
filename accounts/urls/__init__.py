from .auth_urls import auth_urls
from .account_urls import account_urls


urlpatterns = auth_urls+account_urls
