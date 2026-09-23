from django.core.management.base import BaseCommand

from toolbox import tree
from toolbox.models import Action, Category, SiteSettings, Step

INTRO = (
    "به پلتفرمی رایگان خوش آمدید که به شما کمک می‌کند قطعه‌کدها، دستورات و فرمان‌های "
    "موردنیاز خود را به شکلی ساده و منظم ذخیره و مدیریت کنید.\n\n"
    "در این وب‌سایت می‌توانید دسته‌بندی‌های دلخواه خود را ایجاد کرده و اطلاعاتتان را در قالب "
    "یک ساختار درختی و منظم سازمان‌دهی کنید. از دستورات کاربردی ترمینال و قطعه‌کدهای "
    "برنامه‌نویسی گرفته تا تنظیمات سرور و کدهایی که به‌طور مکرر استفاده می‌کنید، همه‌چیز "
    "می‌تواند در یک محیط مرتب و قابل دسترس نگهداری شود.\n\n"
    "هر عمل یک درخت است و می‌توانید همان درخت را داخل فلوهای دیگر استفاده کنید؛ "
    "دیگر لازم نیست دستورات را در ورد بنویسید."
)


def add_cmd(parent, order, title, body, language="bash", notes=""):
    Step.objects.create(
        parent=parent,
        order=order,
        kind=Step.KIND_COMMAND,
        title=title,
        body=body.strip() + "\n",
        language=language,
        notes=notes,
    )


def add_nested(parent, order, nested, title=""):
    Step.objects.create(
        parent=parent,
        order=order,
        kind=Step.KIND_ACTION,
        nested=nested,
        title=title,
    )


class Command(BaseCommand):
    help = "Seed demo categories, reusable actions and a sample flow."

    def handle(self, *args, **options):
        tree.DISABLE_SIGNALS = True
        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        if not settings.intro:
            settings.site_name = "کدتولز"
            settings.tagline = "فلو بساز، درخت‌ها را دوباره استفاده کن، با یک کلیک پیدا کن"
            settings.intro = INTRO
            settings.save()

        if Category.objects.exists():
            tree.DISABLE_SIGNALS = False
            tree.invalidate_all()
            self.stdout.write("Content already exists; cache rebuilt.")
            return

        linux = Category.objects.create(name="لینوکس و سرور", icon="🖥️", description="نصب، فایروال، سرویس‌ها", order=0)
        docker = Category.objects.create(name="داکر", icon="🐳", description="کانتینر و کامپوز", order=1)
        django = Category.objects.create(name="جنگو", icon="🌿", description="پروژه و دیپلوی", order=2)
        git = Category.objects.create(name="گیت", icon="🔀", description="نسخه‌کنترل روزمره", order=3)

        install_docker = Action.objects.create(
            title="نصب Docker",
            summary="نصب موتور داکر و Compose روی اوبونتو.",
            category=docker,
            tags="docker, ubuntu",
            is_library=True,
            is_flow=False,
        )
        add_cmd(install_docker, 1, "بسته‌های پیش‌نیاز", """sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg""")
        add_cmd(install_docker, 2, "کلید و مخزن", """sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg""")
        add_cmd(install_docker, 3, "نصب Docker Engine", """sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER""")

        install_nginx = Action.objects.create(
            title="نصب Nginx",
            summary="نصب و فعال‌سازی Nginx.",
            category=linux,
            tags="nginx, web",
            is_library=True,
        )
        add_cmd(install_nginx, 1, "نصب", "sudo apt-get update && sudo apt-get install -y nginx")
        add_cmd(install_nginx, 2, "فعال‌سازی", """sudo systemctl enable --now nginx
sudo nginx -t""")

        ufw = Action.objects.create(
            title="فایروال UFW",
            summary="باز کردن پورت‌های وب و SSH.",
            category=linux,
            tags="ufw, firewall",
            is_library=True,
        )
        add_cmd(ufw, 1, "قوانین", """sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status""")

        git_daily = Action.objects.create(
            title="گیت روزمره",
            summary="دستورات پرتکرار گیت.",
            category=git,
            tags="git",
            is_library=True,
        )
        add_cmd(git_daily, 1, "وضعیت و استیج", """git status
git add -A
git commit -m "پیام کامیت" """, language="git")
        add_cmd(git_daily, 2, "ارسال", "git push -u origin HEAD", language="git")

        django_new = Action.objects.create(
            title="ساخت پروژه جنگو",
            summary="شروع یک پروژه Django با venv.",
            category=django,
            tags="django, python",
            is_library=True,
        )
        add_cmd(django_new, 1, "محیط مجازی", """python3 -m venv .venv
source .venv/bin/activate
pip install Django psycopg2-binary gunicorn""", language="bash")
        add_cmd(django_new, 2, "شروع پروژه", """django-admin startproject config .
python manage.py startapp core
python manage.py migrate""", language="bash")

        server_flow = Action.objects.create(
            title="راه‌اندازی سرور اوبونتو",
            summary="یک فلو کامل: فایروال، داکر و Nginx. هر بخش یک درخت جداست و جای دیگر هم قابل استفاده است.",
            category=linux,
            tags="سرور, ubuntu, شروع",
            is_flow=True,
            is_library=True,
        )
        add_cmd(
            server_flow,
            1,
            "به‌روزرسانی سیستم",
            "sudo apt-get update && sudo apt-get upgrade -y",
            notes="اولین کاری که روی سرور تازه انجام می‌دهید.",
        )
        add_nested(server_flow, 2, ufw)
        add_nested(server_flow, 3, install_docker)
        add_nested(server_flow, 4, install_nginx)

        deploy_flow = Action.objects.create(
            title="دیپلوی جنگو با Docker",
            summary="فلو دیپلوی: پروژه جنگو + داکر.",
            category=django,
            tags="deploy, docker, django",
            is_flow=True,
            is_library=True,
        )
        add_nested(deploy_flow, 1, django_new)
        add_nested(deploy_flow, 2, install_docker)
        add_cmd(
            deploy_flow,
            3,
            "بالا آوردن استک",
            "docker compose up --build -d\ndocker compose ps",
            notes="از ریشه پروژه‌ای که compose دارد اجرا کنید.",
        )

        tree.DISABLE_SIGNALS = False
        tree.invalidate_all()
        self.stdout.write(self.style.SUCCESS("Sample flows and reusable actions seeded."))
