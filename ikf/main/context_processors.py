from .forms import ContactUsForm

def contact_form_context(request):
    return {'contact_form': ContactUsForm()}

from .models import PageContent

def page_media(request):
    key = getattr(request.resolver_match, "url_name", None)
    if not key:
        return {}

    page = (
        PageContent.objects
        .prefetch_related("images")
        .filter(page_key=key)
        .first()
    )

    images = list(page.images.filter(is_active=True)) if page else []

    return {
        "page_content": page,
        "page_images": images,
        "hero_image": images[0] if images else None,
    }
