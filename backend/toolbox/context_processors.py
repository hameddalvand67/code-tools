from . import tree


def chrome(request):
    return {
        "site": tree.get_settings(),
        "nav_categories": tree.get_categories(),
    }
