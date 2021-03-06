# Generated by Django 2.2.16 on 2020-11-11 12:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lists', '0002_auto_20201026_1413'),
        ('blog', '0002_auto_20201027_1815'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='electnew',
            options={'ordering': ['-created'], 'verbose_name': 'Запись о чиновнике', 'verbose_name_plural': 'Лента чиновника'},
        ),
        migrations.RemoveField(
            model_name='blog',
            name='category',
        ),
        migrations.RemoveField(
            model_name='electnew',
            name='content',
        ),
        migrations.RemoveField(
            model_name='electnew',
            name='image',
        ),
        migrations.AddField(
            model_name='electnew',
            name='creator',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Создатель'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='electnew',
            name='status',
            field=models.CharField(choices=[('D', 'Черновик'), ('PG', 'Обработка'), ('P', 'Опубликована')], default='P', max_length=2, verbose_name='Статус записи'),
        ),
        migrations.RemoveField(
            model_name='electnew',
            name='category',
        ),
        migrations.AddField(
            model_name='electnew',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='elect_cat', to='lists.BlogCategory', verbose_name='Категория записи чиновника'),
        ),
        migrations.AlterField(
            model_name='electnew',
            name='elect',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='new_elect', to='elect.Elect', verbose_name='Чиновник'),
        ),
        migrations.CreateModel(
            name='ElectVotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(choices=[(-1, 'Не нравится'), (1, 'Нравится')], default=0, verbose_name='Голос')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.ElectNew')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
