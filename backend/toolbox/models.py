from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TimeStamped(models.Model):
    created_at = models.DateTimeField("ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("ویرایش", auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(TimeStamped):
    site_name = models.CharField("نام سایت", max_length=80, default="کدتولز")
    tagline = models.CharField("شعار", max_length=180, blank=True)
    intro = models.TextField("متن خوش‌آمد", blank=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return None

    def __str__(self):
        return self.site_name


class Category(TimeStamped):
    name = models.CharField("نام دسته", max_length=80)
    slug = models.SlugField("اسلاگ", max_length=100, unique=True, allow_unicode=True, blank=True)
    description = models.CharField("توضیح کوتاه", max_length=220, blank=True)
    icon = models.CharField("آیکون", max_length=8, blank=True, default="📁")
    order = models.PositiveIntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "دسته"
        verbose_name_plural = "دسته‌ها"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or f"cat-{self.pk or 'new'}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", args=[self.slug])


class Action(TimeStamped):
    """یک درخت قابل استفاده مجدد: فلو یا زیرعمل."""

    title = models.CharField("عنوان عمل / فلو", max_length=180)
    slug = models.SlugField("اسلاگ", max_length=200, unique=True, allow_unicode=True, blank=True)
    summary = models.TextField("خلاصه", blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name="دسته",
        related_name="actions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.CharField("برچسب‌ها", max_length=220, blank=True, help_text="با ویرگول جدا کنید")
    is_flow = models.BooleanField(
        "فلو (نمایش در صفحه اصلی)",
        default=False,
        help_text="اگر روشن باشد، این درخت به‌عنوان یک فلو در صفحه اصلی دیده می‌شود.",
    )
    is_library = models.BooleanField(
        "قابل استفاده در درخت‌های دیگر",
        default=True,
        help_text="می‌توان این عمل را به‌عنوان زیرعمل در هر فلو یا عمل دیگری گذاشت.",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "عمل / فلو"
        verbose_name_plural = "عمل‌ها و فلوها"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True) or "action"
            slug = base
            i = 2
            while Action.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("action", args=[self.slug])

    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class Step(TimeStamped):
    KIND_COMMAND = "command"
    KIND_ACTION = "action"
    KIND_CHOICES = (
        (KIND_COMMAND, "دستور / قطعه‌کد"),
        (KIND_ACTION, "زیرعمل (درخت دیگر)"),
    )
    LANG_CHOICES = (
        ("bash", "Bash / ترمینال"),
        ("python", "Python"),
        ("javascript", "JavaScript"),
        ("nginx", "Nginx"),
        ("sql", "SQL"),
        ("yaml", "YAML"),
        ("json", "JSON"),
        ("dockerfile", "Dockerfile"),
        ("git", "Git"),
        ("text", "متن"),
    )

    parent = models.ForeignKey(
        Action,
        verbose_name="عمل والد",
        related_name="steps",
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField("ترتیب", default=0)
    kind = models.CharField("نوع", max_length=16, choices=KIND_CHOICES, default=KIND_COMMAND)
    title = models.CharField("عنوان گام", max_length=180, blank=True)
    language = models.CharField("زبان", max_length=20, choices=LANG_CHOICES, default="bash", blank=True)
    body = models.TextField("دستور / کد", blank=True)
    notes = models.TextField("یادداشت", blank=True)
    nested = models.ForeignKey(
        Action,
        verbose_name="درخت ارجاع‌شده",
        related_name="used_in_steps",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "گام"
        verbose_name_plural = "گام‌ها"

    def __str__(self):
        return self.display_title

    @property
    def display_title(self):
        if self.title:
            return self.title
        if self.kind == self.KIND_ACTION and self.nested_id:
            return self.nested.title
        if self.body:
            return self.body.strip().splitlines()[0][:80]
        return "گام بدون عنوان"

    def clean(self):
        body = (self.body or "").strip()
        if self.kind == self.KIND_COMMAND and not body:
            raise ValidationError({"body": "برای گام دستوری، متن دستور را بنویسید."})
        if self.kind == self.KIND_ACTION:
            nested_id = self.nested_id or getattr(self.nested, "pk", None)
            if not nested_id:
                raise ValidationError({"nested": "یک عمل موجود را برای زیرعمل انتخاب کنید."})
            if nested_id == self.parent_id:
                raise ValidationError({"nested": "نمی‌توان یک عمل را داخل خودش گذاشت."})
            if would_create_cycle(self.parent_id, nested_id):
                raise ValidationError({"nested": "این ارجاع حلقه می‌سازد؛ درخت دیگری انتخاب کنید."})


def would_create_cycle(parent_id: int | None, nested_id: int | None) -> bool:
    if not parent_id or not nested_id:
        return False
    if parent_id == nested_id:
        return True
    seen = {nested_id}
    queue = [nested_id]
    while queue:
        current = queue.pop()
        child_ids = Step.objects.filter(parent_id=current, kind=Step.KIND_ACTION, nested_id__isnull=False).values_list(
            "nested_id", flat=True
        )
        for child_id in child_ids:
            if child_id == parent_id:
                return True
            if child_id not in seen:
                seen.add(child_id)
                queue.append(child_id)
    return False
