from accounts.account.models import (Account)
from django.http import HttpRequest


def account(request: HttpRequest):
    account = None
    if request.user.is_authenticated:
        account_qs = Account.objects.filter(user=request.user)
        if account_qs.exists():
            account = account_qs.first()
        account = account
    return {'account': account}
