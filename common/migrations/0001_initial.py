# Generated by Django 3.1.5 on 2021-02-21 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneCodes',
            fields=[
                ('phone', models.CharField(max_length=15, verbose_name='Телефон')),
                ('code', models.PositiveSmallIntegerField(default=0, verbose_name='Код')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
        ),
    ]
