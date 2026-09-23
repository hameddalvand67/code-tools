from django.db.models import Count, Q
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ActionForm, CategoryForm, CommandStepForm, NestedStepForm
from .models import Action, Category, Step
from . import tree


@require_GET
def health(request):
    return JsonResponse({"ok": True, "service": "code-tools"})


def home(request):
    q = (request.GET.get("q") or "").strip()
    settings = tree.get_settings()
    categories = tree.get_categories()
    flows = Action.objects.filter(is_flow=True).select_related("category")
    library = Action.objects.filter(is_library=True).select_related("category")[:12]
    results = None
    if q:
        results = (
            Action.objects.filter(
                Q(title__icontains=q)
                | Q(summary__icontains=q)
                | Q(tags__icontains=q)
                | Q(steps__body__icontains=q)
                | Q(steps__title__icontains=q)
            )
            .select_related("category")
            .distinct()
        )
    return render(
        request,
        "toolbox/home.html",
        {
            "settings": settings,
            "categories": categories,
            "flows": flows,
            "library": library,
            "q": q,
            "results": results,
        },
    )


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    actions = category.actions.select_related("category").all()
    return render(request, "toolbox/category.html", {"category": category, "actions": actions})


def library(request):
    actions = Action.objects.filter(is_library=True).select_related("category").annotate(step_count=Count("steps"))
    return render(request, "toolbox/library.html", {"actions": actions})


def action_detail(request, slug):
    action = get_object_or_404(Action.objects.select_related("category"), slug=slug)
    nodes = tree.get_tree(action)
    used_in = action.used_in_steps.select_related("parent").all()
    return render(
        request,
        "toolbox/action.html",
        {
            "action": action,
            "nodes": nodes,
            "flat": tree.get_flat(action),
            "used_in": used_in,
            "view": request.GET.get("view") or "tree",
        },
    )


@require_GET
def search_api(request):
    q = (request.GET.get("q") or "").strip()
    qs = Action.objects.all()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(tags__icontains=q) | Q(summary__icontains=q))
    data = [
        {
            "title": a.title,
            "slug": a.slug,
            "url": a.get_absolute_url(),
            "is_flow": a.is_flow,
            "category": a.category.name if a.category else "",
        }
        for a in qs.select_related("category")[:20]
    ]
    return JsonResponse({"results": data})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = "input"
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "home")
    return render(request, "toolbox/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
@require_http_methods(["GET", "POST"])
def action_create(request):
    form = ActionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        action = form.save()
        messages.success(request, "عمل ساخته شد. حالا گام‌ها را اضافه کنید.")
        return redirect("action_edit", slug=action.slug)
    return render(request, "toolbox/action_form.html", {"form": form, "action": None})


@login_required
@require_http_methods(["GET", "POST"])
def action_edit(request, slug):
    action = get_object_or_404(Action, slug=slug)
    form = ActionForm(request.POST or None, instance=action)
    cmd_form = CommandStepForm()
    nest_form = NestedStepForm(parent=action)
    if request.method == "POST" and "save_meta" in request.POST and form.is_valid():
        form.save()
        messages.success(request, "اطلاعات عمل ذخیره شد.")
        return redirect("action_edit", slug=action.slug)
    return render(
        request,
        "toolbox/action_form.html",
        {
            "form": form,
            "action": action,
            "cmd_form": cmd_form,
            "nest_form": nest_form,
            "steps": action.steps.select_related("nested"),
        },
    )


@login_required
@require_POST
def add_command(request, slug):
    action = get_object_or_404(Action, slug=slug)
    form = CommandStepForm(request.POST)
    if form.is_valid():
        step = form.save(commit=False)
        step.parent = action
        step.order = (action.steps.order_by("-order").values_list("order", flat=True).first() or 0) + 1
        step.save()
        messages.success(request, "دستور اضافه شد.")
    else:
        messages.error(request, "دستور ذخیره نشد. متن را بررسی کنید.")
    return redirect("action_edit", slug=action.slug)


@login_required
@require_POST
def add_nested(request, slug):
    action = get_object_or_404(Action, slug=slug)
    form = NestedStepForm(request.POST, parent=action)
    if form.is_valid():
        step = form.save(commit=False)
        step.parent = action
        step.order = (action.steps.order_by("-order").values_list("order", flat=True).first() or 0) + 1
        step.save()
        messages.success(request, "زیرعمل به درخت اضافه شد.")
    else:
        messages.error(request, form.errors.as_text() or "این زیرعمل قابل افزودن نیست.")
    return redirect("action_edit", slug=action.slug)


@login_required
@require_POST
def delete_step(request, pk):
    step = get_object_or_404(Step, pk=pk)
    slug = step.parent.slug
    step.delete()
    messages.success(request, "گام حذف شد.")
    return redirect("action_edit", slug=slug)


@login_required
@require_POST
def move_step(request, pk, direction):
    step = get_object_or_404(Step, pk=pk)
    siblings = list(step.parent.steps.all())
    idx = next(i for i, s in enumerate(siblings) if s.pk == step.pk)
    swap_with = idx - 1 if direction == "up" else idx + 1
    if 0 <= swap_with < len(siblings):
        other = siblings[swap_with]
        step.order, other.order = other.order, step.order
        step.save(update_fields=["order"])
        other.save(update_fields=["order"])
    return redirect("action_edit", slug=step.parent.slug)


@login_required
@require_POST
def delete_action(request, slug):
    action = get_object_or_404(Action, slug=slug)
    action.delete()
    messages.success(request, "عمل حذف شد.")
    return redirect("home")


@login_required
@require_http_methods(["GET", "POST"])
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "دسته ساخته شد.")
        return redirect("home")
    return render(request, "toolbox/category_form.html", {"form": form})
