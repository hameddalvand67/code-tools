from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from . import tree
from .models import Action, Category, SiteSettings, Step


@receiver([post_save, post_delete], sender=SiteSettings)
@receiver([post_save, post_delete], sender=Category)
@receiver([post_save, post_delete], sender=Action)
@receiver([post_save, post_delete], sender=Step)
def content_changed(sender, **kwargs):
    if getattr(tree, "DISABLE_SIGNALS", False):
        return
    tree.invalidate_all()
