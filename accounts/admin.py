from django.contrib import admin
from accounts.models import (Account,  AccountEmail, SocialMethod,

                             )


admin.site.register(Account)
admin.site.register(AccountEmail)
admin.site.register(SocialMethod)
