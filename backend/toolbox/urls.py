from django.urls import path, register_converter

from . import views


class UnicodeSlugConverter:
    regex = r"[-\w]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(UnicodeSlugConverter, "uslug")

urlpatterns = [
    path("health/", views.health, name="health"),
    path("", views.home, name="home"),
    path("library/", views.library, name="library"),
    path("c/<uslug:slug>/", views.category_detail, name="category"),
    path("a/<uslug:slug>/", views.action_detail, name="action"),
    path("api/search/", views.search_api, name="search_api"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("new/", views.action_create, name="action_create"),
    path("new-category/", views.category_create, name="category_create"),
    path("a/<uslug:slug>/edit/", views.action_edit, name="action_edit"),
    path("a/<uslug:slug>/add-command/", views.add_command, name="add_command"),
    path("a/<uslug:slug>/add-nested/", views.add_nested, name="add_nested"),
    path("a/<uslug:slug>/delete/", views.delete_action, name="delete_action"),
    path("step/<int:pk>/delete/", views.delete_step, name="delete_step"),
    path("step/<int:pk>/move/<str:direction>/", views.move_step, name="move_step"),
]
