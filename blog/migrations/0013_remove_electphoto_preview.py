# Generated by Django 2.2.16 on 2020-11-29 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_auto_20201129_1543'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electphoto',
            name='preview',
        ),
    ]
