# Generated by Django 3.2.16 on 2023-05-27 16:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0005_alter_post_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="image_exists",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="post",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="post_images/"
            ),
        ),
    ]
