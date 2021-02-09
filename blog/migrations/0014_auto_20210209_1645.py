# Generated by Django 3.1.5 on 2021-02-09 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elect', '0007_auto_20201111_1901'),
        ('blog', '0013_remove_electphoto_preview'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electnew',
            name='elect',
        ),
        migrations.AddField(
            model_name='electnew',
            name='elect',
            field=models.ManyToManyField(blank=True, related_name='new_elect', to='elect.Elect', verbose_name='Чиновник'),
        ),
    ]
