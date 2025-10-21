from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from django.contrib.auth import get_user_model
        from main.models import Role, UserRole

        try:
            if not Role.objects.exists():
                roles_in_order = [
                    ('MasterAdmin', 'Главный администратор'),
                    ('SPbUAdmin', 'Администратор СПбГУ'),
                    ('POMIAdmin', 'Администратор ПОМИ'),
                    ('SPbUUser', 'Пользователь СПбГУ'),
                    ('POMIUser', 'Пользователь ПОМИ'),
                ]

                for index, (name, _) in enumerate(roles_in_order, start=1):
                    Role.objects.get_or_create(id=index, name=name)

            User = get_user_model()

            master_username = "master"
            master_password = "euleradmin123"

            master_user, created = User.objects.get_or_create(
                username=master_username,
                defaults={
                    "first_name_rus": "Мастер",
                    "second_name_rus": "Админ",
                    "group": "SPbU",
                    "email": 'masteradmin@example.com',
                }
            )

            if created:
                master_user.set_password(master_password)
                master_user.save()

            master_role = Role.objects.get(name="MasterAdmin")
            UserRole.objects.get_or_create(user=master_user, role=master_role)

        except (OperationalError, ProgrammingError):
            pass
