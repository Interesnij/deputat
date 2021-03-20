# Generated by Django 3.1.5 on 2021-03-20 12:32

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('verb', models.CharField(choices=[('ITE', ' разместил'), ('COM', ' оставил'), ('WCOM', ' оставила'), ('GCOM', ' оставили'), ('REP', ' ответил на'), ('WREP', ' ответила на'), ('GREP', ' ответили на'), ('LIK', ' оценил'), ('WLIK', ' оценила'), ('GLIK', ' оценили'), ('DIS', ' не оценил'), ('WDIS', ' не оценила'), ('GDIS', ' не оценили'), ('LCO', ' оценил'), ('WLCO', ' оценила '), ('GLCO', ' оценили'), ('LRE', ' оценил'), ('WLRE', ' оценила'), ('GLRE', ' оценили'), ('SVO', ' участвовал в опросе'), ('WSVO', ' участвовала в опросе'), ('GSVO', ' участвовали в опросе'), ('CRE', ' подал заявку в'), ('WCRE', ' подала заявку в'), ('GCRE', ' подали заявку в'), ('CCO', ' принят в'), ('WCCO', ' принята'), ('GCCO', ' приняты'), ('REG', ' зарегистрировался'), ('WREG', ' зарегистрировалась'), ('GREG', ' зарегистрировались')], max_length=5, verbose_name='Тип уведомления')),
                ('status', models.CharField(choices=[('U', 'Не прочитано'), ('R', 'Прочитано'), ('D', 'Удалено')], default='U', max_length=1, verbose_name='Статус')),
                ('attach', models.CharField(max_length=30, verbose_name='Объект')),
            ],
            options={
                'verbose_name': 'Уведомление',
                'verbose_name_plural': 'Уведомления',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='UserNewsNotify',
            fields=[
                ('user', models.PositiveIntegerField(default=0, verbose_name='Кто подписывается')),
                ('target', models.PositiveIntegerField(default=0, verbose_name='На кого подписывается')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Новости по по факту дружбы или подписки в друзья',
                'verbose_name_plural': 'Новости по по факту дружбы или подписки в друзья',
            },
        ),
        migrations.CreateModel(
            name='UserProfileNotify',
            fields=[
                ('user', models.PositiveIntegerField(default=0, verbose_name='Кто подписывается')),
                ('target', models.PositiveIntegerField(default=0, verbose_name='На кого подписывается')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'уведомления при подписке на уведосления пользователя',
                'verbose_name_plural': 'уведомления при подписке на уведосления пользователя',
            },
        ),
        migrations.AddIndex(
            model_name='userprofilenotify',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created'], name='notify_user_created_7af348_brin'),
        ),
        migrations.AddIndex(
            model_name='usernewsnotify',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created'], name='notify_user_created_9028a5_brin'),
        ),
        migrations.AddField(
            model_name='notify',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Инициатор'),
        ),
        migrations.AddField(
            model_name='notify',
            name='object_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='notify.notify', verbose_name='Например, несколько человек лайкает пост. Нужно для группировки'),
        ),
        migrations.AddField(
            model_name='notify',
            name='recipient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Получатель'),
        ),
        migrations.AddField(
            model_name='notify',
            name='user_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='notify.notify', verbose_name='Например, человек лайкает несколько постов. Нужно для группировки'),
        ),
        migrations.AddIndex(
            model_name='notify',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created'], name='notify_noti_created_9feff9_brin'),
        ),
    ]
