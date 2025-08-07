from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from zoneinfo import ZoneInfo
from django.contrib.gis.geoip2 import GeoIP2
from django.conf import settings
from django.http import HttpRequest
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class GeolocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        ip_address = self.get_client_ip(request)
        self.ip_address = ip_address
        # Set a default attribute for ip_address
        request.ip_address = ip_address

        # Set IP info and handle exceptions gracefully
        ip_info = self.get_ip_info(ip_address)
        if ip_info:
            self.set_request_ip_info(request, ip_info)

        # Set timezone based on user or request attributes
        self.set_timezone(request)

        return self.get_response(request)

    def get_client_ip(self, request: HttpRequest) -> str:
        if settings.DEBUG:
            logger.debug("DEBUG mode: Returning test IP address.")
            return "154.47.26.236"

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
            logger.debug(f"Extracted IP from HTTP_X_FORWARDED_FOR: {ip}")
            return ip
        ip = request.META.get('REMOTE_ADDR', '')
        logger.debug(f"Extracted IP from REMOTE_ADDR: {ip}")
        return ip

    def get_ip_info(self, ip_address: str) -> dict:
        if not ip_address:
            logger.warning("No IP address provided for GeoIP lookup.")
            return {}

        cache_key = f"geoip:{ip_address}"
        ip_info = cache.get(cache_key)
        if not ip_info:
            try:
                geo = GeoIP2()
                ip_info = geo.city(ip_address)
                cache.set(cache_key, ip_info, timeout=3600)
                logger.debug(f"GeoIP lookup succeeded for {ip_address}.")
            except Exception as e:
                logger.error(f"GeoIP lookup failed for {ip_address}: {e}")
                ip_info = {}
        return ip_info

    def set_request_ip_info(self, request: HttpRequest, ip_info: dict):
        request.city = ip_info.get('city', None)
        request.continent_code = ip_info.get('continent_code', None)
        request.continent_name = ip_info.get('continent_name', None)
        request.country_code = ip_info.get('country_code', None)
        request.country_name = ip_info.get('country_name', None)
        request.region_name = ip_info.get('region_name', None)
        request.time_zone = ip_info.get('time_zone', None)
        request.latitude = round(ip_info.get('latitude',), 6)
        request.longitude = round(ip_info.get('longitude',), 6)
        request.ip_address = self.ip_address

    def set_timezone(self, request: HttpRequest):
        try:
            if request.user.is_authenticated:
                from accounts.models import Account
                account = Account.objects.filter(user=request.user).first()
                if account and account.timezone:
                    timezone.activate(ZoneInfo(account.timezone))
                    return

            if hasattr(request, 'time_zone') and request.time_zone:
                timezone.activate(ZoneInfo(request.time_zone))
        except ObjectDoesNotExist:
            pass
