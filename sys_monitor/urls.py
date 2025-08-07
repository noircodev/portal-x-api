from django.urls import path
from sys_monitor.views import (system_stats_view, system_info_view)

app_name = "sys_monitor"
urlpatterns = [
    path("info/", system_info_view, name="system_info"),
    path("stats/", system_stats_view, name="system_stats"),

]
