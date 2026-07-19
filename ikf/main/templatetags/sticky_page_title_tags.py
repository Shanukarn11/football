from django import template

from ..models import PageStickyTitle

register = template.Library()


@register.simple_tag(takes_context=True)
def get_sticky_page_title(context):
    """
    Returns the admin-managed sticky title for the current page, or empty
    string when no active override exists. Used by base.html to decide whether
    to override the auto-detected floating page title.
    """
    request = context.get("request")
    url_name = getattr(getattr(request, "resolver_match", None), "url_name", None)
    if not url_name:
        return ""

    try:
        entry = (
            PageStickyTitle.objects
            .filter(url_name=url_name, is_active=True)
            .only("title")
            .first()
        )
    except Exception:
        return ""

    return entry.title if entry else ""
