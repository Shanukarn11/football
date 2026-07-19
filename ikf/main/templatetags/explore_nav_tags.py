from django import template

from ..models import ExploreNav

register = template.Library()


@register.simple_tag(takes_context=True)
def get_explore_nav(context):
    """
    Returns the admin-managed 'Explore More' rail for the current page, or None
    when no active override exists. When None, the template falls back to the
    existing hardcoded rail.

    The returned object gets a ``resolved_links`` attribute: the active links
    with an extra ``is_current_page`` flag already computed, so the template
    can hide the link that points at the page you're already on.
    """
    request = context.get("request")
    resolver = getattr(request, "resolver_match", None)
    url_name = getattr(resolver, "url_name", None)
    if not url_name:
        return None

    slug = ""
    kwargs = getattr(resolver, "kwargs", None)
    if kwargs:
        slug = kwargs.get("slug", "") or ""

    try:
        # 1. A rail that explicitly targets this page wins.
        nav = (
            ExploreNav.objects
            .filter(is_active=True, pages__url_name=url_name)
            .prefetch_related("links")
            .order_by("order", "id")
            .first()
        )
        # 2. Otherwise fall back to a site-wide rail (shown on every page but Home).
        if not nav and url_name != "home":
            nav = (
                ExploreNav.objects
                .filter(is_active=True, apply_to_all_pages=True)
                .prefetch_related("links")
                .order_by("order", "id")
                .first()
            )
    except Exception:
        return None

    if not nav:
        return None

    current_path = getattr(request, "path", "") or ""
    links = [lk for lk in nav.links.all() if lk.is_active]
    links.sort(key=lambda lk: (lk.order, lk.id))
    for lk in links:
        lk.is_current_page = lk.matches_current(url_name, slug, current_path)
    nav.resolved_links = links
    return nav
