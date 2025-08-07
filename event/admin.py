from django.contrib import admin
from event.models import (
    Country,
    Location,
    SearchPhrase,
    Event,
    RecentSearch,
    BetaSubscriber,
    City,
    ZipCode,
    AppVersion,
)


class EventAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description']
    list_display = ['title', 'city__city_name', 'start_date', ]
    list_filter = ['event_source']
    # list_filter = ['start_date', 'valid', 'city']


class CityAdmin(admin.ModelAdmin):
    readonly_fields = ['coords']
    exclude = ['metro_code', 'dma_code', 'area_code',]


class AppVersionAdmin(admin.ModelAdmin):
    list_display = ['version', 'release_date', 'commit_hash', 'commit_branch']
    search_fields = ['version', 'release_notes']
    readonly_fields = ['version', 'release_notes', 'release_date',
                       'commit_hash', 'commit_branch']


admin.site.register(Country)
admin.site.register(Location)
admin.site.register(SearchPhrase)
admin.site.register(Event, EventAdmin)
admin.site.register(RecentSearch)
admin.site.register(BetaSubscriber)
admin.site.register(City, CityAdmin)
admin.site.register(ZipCode)
admin.site.register(AppVersion, AppVersionAdmin)
