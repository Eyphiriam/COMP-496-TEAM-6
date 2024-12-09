# Generated by Django 5.1.2 on 2024-12-08 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UploadedImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="uploads/")),
                ("result", models.CharField(blank=True, max_length=50, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
