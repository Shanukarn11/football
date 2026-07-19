from django import template

register = template.Library()

@register.simple_tag
def query_transform(request_get, new_params):
    dict_ = request_get.copy()
    for param in new_params.split('&'):
        key, value = param.split('=')
        dict_[key] = value
    return dict_.urlencode()
