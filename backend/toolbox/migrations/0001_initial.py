# Generated for toolbox

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="ویرایش")),
                ("site_name", models.CharField(default="کدتولز", max_length=80, verbose_name="نام سایت")),
                ("tagline", models.CharField(blank=True, max_length=180, verbose_name="شعار")),
                ("intro", models.TextField(blank=True, verbose_name="متن خوش‌آمد")),
            ],
            options={"verbose_name": "تنظیمات سایت", "verbose_name_plural": "تنظیمات سایت"},
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="ویرایش")),
                ("name", models.CharField(max_length=80, verbose_name="نام دسته")),
                ("slug", models.SlugField(allow_unicode=True, blank=True, max_length=100, unique=True, verbose_name="اسلاگ")),
                ("description", models.CharField(blank=True, max_length=220, verbose_name="توضیح کوتاه")),
                ("icon", models.CharField(blank=True, default="📁", max_length=8, verbose_name="آیکون")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
            ],
            options={"verbose_name": "دسته", "verbose_name_plural": "دسته‌ها", "ordering": ["order", "id"]},
        ),
        migrations.CreateModel(
            name="Action",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="ویرایش")),
                ("title", models.CharField(max_length=180, verbose_name="عنوان عمل / فلو")),
                ("slug", models.SlugField(allow_unicode=True, blank=True, max_length=200, unique=True, verbose_name="اسلاگ")),
                ("summary", models.TextField(blank=True, verbose_name="خلاصه")),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="actions", to="toolbox.category", verbose_name="دسته")),
                ("tags", models.CharField(blank=True, help_text="با ویرگول جدا کنید", max_length=220, verbose_name="برچسب‌ها")),
                ("is_flow", models.BooleanField(default=False, help_text="اگر روشن باشد، این درخت به‌عنوان یک فلو در صفحه اصلی دیده می‌شود.", verbose_name="فلو (نمایش در صفحه اصلی)")),
                ("is_library", models.BooleanField(default=True, help_text="می‌توان این عمل را به‌عنوان زیرعمل در هر فلو یا عمل دیگری گذاشت.", verbose_name="قابل استفاده در درخت‌های دیگر")),
            ],
            options={"verbose_name": "عمل / فلو", "verbose_name_plural": "عمل‌ها و فلوها", "ordering": ["title"]},
        ),
        migrations.CreateModel(
            name="Step",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="ویرایش")),
                ("parent", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="steps", to="toolbox.action", verbose_name="عمل والد")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("kind", models.CharField(choices=[("command", "دستور / قطعه‌کد"), ("action", "زیرعمل (درخت دیگر)")], default="command", max_length=16, verbose_name="نوع")),
                ("title", models.CharField(blank=True, max_length=180, verbose_name="عنوان گام")),
                ("language", models.CharField(blank=True, choices=[("bash", "Bash / ترمینال"), ("python", "Python"), ("javascript", "JavaScript"), ("nginx", "Nginx"), ("sql", "SQL"), ("yaml", "YAML"), ("json", "JSON"), ("dockerfile", "Dockerfile"), ("git", "Git"), ("text", "متن")], default="bash", max_length=20, verbose_name="زبان")),
                ("body", models.TextField(blank=True, verbose_name="دستور / کد")),
                ("notes", models.TextField(blank=True, verbose_name="یادداشت")),
                ("nested", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="used_in_steps", to="toolbox.action", verbose_name="درخت ارجاع‌شده")),
            ],
            options={"verbose_name": "گام", "verbose_name_plural": "گام‌ها", "ordering": ["order", "id"]},
        ),
    ]
