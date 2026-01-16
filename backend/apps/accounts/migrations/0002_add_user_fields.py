from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                upload_to="avatars/%Y/%m/",
                blank=True,
                null=True,
                verbose_name="Avatar",
                help_text="Profil rasmi",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=False, verbose_name="Tasdiqlangan", help_text="Email manzili tasdiqlangan yoki yo'q"),
        ),
        migrations.AddField(
            model_name="user",
            name="last_activity",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Oxirgi faollik", help_text="Foydalanuvchining oxirgi faollik vaqti"),
        ),
        migrations.AddField(
            model_name="user",
            name="employee",
            field=models.OneToOneField(
                to="employees.Employee",
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                related_name="user_account",
                verbose_name="Bog'langan hodim",
                help_text="Agar foydalanuvchi hodim bo'lsa, uning profili",
            ),
        ),
    ]
