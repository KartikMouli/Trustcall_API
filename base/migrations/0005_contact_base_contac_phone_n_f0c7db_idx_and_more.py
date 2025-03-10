# Generated by Django 5.1.2 on 2024-12-26 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_user_email'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['phone_number'], name='base_contac_phone_n_f0c7db_idx'),
        ),
        migrations.AddIndex(
            model_name='globalphonebook',
            index=models.Index(fields=['phone_number'], name='base_global_phone_n_e8d73a_idx'),
        ),
        migrations.AddIndex(
            model_name='spamrecord',
            index=models.Index(fields=['phone_number'], name='base_spamre_phone_n_973441_idx'),
        ),
        migrations.AddIndex(
            model_name='spamreport',
            index=models.Index(fields=['user', 'phone_number'], name='base_spamre_user_id_7e347d_idx'),
        ),
    ]
