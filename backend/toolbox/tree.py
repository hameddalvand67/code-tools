from django.core.cache import cache

from .models import Action, Category, SiteSettings, Step

DISABLE_SIGNALS = False
SETTINGS_KEY = "settings"
NAV_KEY = "nav"
TREE_PREFIX = "tree:"
FLAT_PREFIX = "flat:"


def invalidate_all():
    cache.delete_many([SETTINGS_KEY, NAV_KEY])
    cache.delete_many([f"{TREE_PREFIX}{pk}" for pk in Action.objects.values_list("pk", flat=True)])
    cache.delete_many([f"{FLAT_PREFIX}{pk}" for pk in Action.objects.values_list("pk", flat=True)])


def get_settings() -> dict:
    data = cache.get(SETTINGS_KEY)
    if data is None:
        obj, _ = SiteSettings.objects.get_or_create(pk=1)
        data = {"site_name": obj.site_name, "tagline": obj.tagline, "intro": obj.intro}
        cache.set(SETTINGS_KEY, data)
    return data


def get_categories():
    data = cache.get(NAV_KEY)
    if data is None:
        data = [
            {
                "name": c.name,
                "slug": c.slug,
                "icon": c.icon,
                "description": c.description,
                "count": c.actions.count(),
            }
            for c in Category.objects.all()
        ]
        cache.set(NAV_KEY, data)
    return data


def _step_dict(step: Step, trail: list[int]) -> dict:
    item = {
        "id": step.id,
        "kind": step.kind,
        "title": step.display_title,
        "language": step.language,
        "body": step.body,
        "notes": step.notes,
        "nested_slug": "",
        "nested_title": "",
        "children": [],
        "cycle": False,
    }
    if step.kind == Step.KIND_ACTION and step.nested_id:
        item["nested_slug"] = step.nested.slug
        item["nested_title"] = step.nested.title
        if step.nested_id in trail:
            item["cycle"] = True
        else:
            item["children"] = _action_steps(step.nested, trail + [step.nested_id])
    return item


def _action_steps(action: Action, trail: list[int]) -> list[dict]:
    steps = action.steps.select_related("nested").all()
    return [_step_dict(s, trail) for s in steps]


def get_tree(action: Action) -> list[dict]:
    key = f"{TREE_PREFIX}{action.pk}"
    data = cache.get(key)
    if data is None:
        data = _action_steps(action, [action.pk])
        cache.set(key, data)
    return data


def flatten_tree(nodes: list[dict]) -> list[dict]:
    out = []
    for node in nodes:
        if node["kind"] == Step.KIND_COMMAND and node.get("body"):
            out.append(node)
        if node.get("children") and not node.get("cycle"):
            out.extend(flatten_tree(node["children"]))
    return out


def get_flat(action: Action) -> list[dict]:
    key = f"{FLAT_PREFIX}{action.pk}"
    data = cache.get(key)
    if data is None:
        data = flatten_tree(get_tree(action))
        cache.set(key, data)
    return data
