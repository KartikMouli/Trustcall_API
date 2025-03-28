# Generated by Django 5.1.2 on 2024-12-26 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_user_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, default=123, max_length=254, verbose_name='email address'),
            preserve_default=False,
        ),
    ]
