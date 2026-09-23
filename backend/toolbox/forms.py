from django import forms

from .models import Action, Category, Step, would_create_cycle


class ActionForm(forms.ModelForm):
    class Meta:
        model = Action
        fields = ("title", "summary", "category", "tags", "is_flow", "is_library")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً راه‌اندازی سرور"}),
            "summary": forms.Textarea(attrs={"rows": 3, "placeholder": "این فلو چه کاری را تمام می‌کند؟"}),
            "tags": forms.TextInput(attrs={"placeholder": "لینوکس، داکر، nginx"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class CommandStepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ("title", "language", "body", "notes")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً نصب Docker"}),
            "body": forms.Textarea(attrs={"rows": 6, "placeholder": "دستور یا قطعه‌کد...", "dir": "ltr", "spellcheck": "false"}),
            "notes": forms.Textarea(attrs={"rows": 2, "placeholder": "توضیح کوتاه اختیاری"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.kind = Step.KIND_COMMAND
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"
        self.fields["body"].widget.attrs["class"] = "input code-input"
        self.fields["body"].required = True

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.kind = Step.KIND_COMMAND
        if commit:
            obj.save()
        return obj


class NestedStepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ("title", "nested")

    def __init__(self, *args, parent=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.instance.kind = Step.KIND_ACTION
        if parent is not None:
            self.instance.parent = parent
        qs = Action.objects.filter(is_library=True).order_by("title")
        if parent and parent.pk:
            qs = qs.exclude(pk=parent.pk)
        self.fields["nested"].queryset = qs
        self.fields["nested"].required = True
        self.fields["nested"].empty_label = "یک عمل انتخاب کنید"
        self.fields["nested"].label = "عمل موجود"
        self.fields["title"].required = False
        self.fields["title"].widget.attrs["placeholder"] = "عنوان نمایشی اختیاری"
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"

    def clean_nested(self):
        nested = self.cleaned_data["nested"]
        parent = self.parent
        if parent and nested and would_create_cycle(parent.pk, nested.pk):
            raise forms.ValidationError("این ارجاع حلقه می‌سازد.")
        return nested

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.kind = Step.KIND_ACTION
        if commit:
            obj.save()
        return obj


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "icon", "description", "order")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"
