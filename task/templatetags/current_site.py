from django.conf import settings
from django.contrib.sites.models import Site
from django import template
register = template.Library()

COMPANY_ADDRESS = "Enugu, Nigeria"


@register.simple_tag(takes_context=True)
def current_domain(context):
    site = Site.objects.get_current()
    domain = f"https://{site.domain}"
    return domain


@register.simple_tag()
def current_site_name():
    site = Site.objects.get_current()
    return site.name


@register.simple_tag()
def customer_support_email():
    site = Site.objects.get_current()
    return f'support@{site.domain}'


@register.simple_tag()
def current_site_address():
    return COMPANY_ADDRESS
