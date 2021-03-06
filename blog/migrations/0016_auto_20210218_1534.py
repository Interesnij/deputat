# Generated by Django 3.1.5 on 2021-02-18 15:34

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0015_auto_20210211_1656'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogcomment',
            old_name='blog_comment',
            new_name='blog',
        ),
        migrations.RenameField(
            model_name='blogcomment',
            old_name='parent_comment',
            new_name='parent',
        ),
        migrations.RenameField(
            model_name='blogcommentvotes',
            old_name='item',
            new_name='blog',
        ),
        migrations.RenameField(
            model_name='blogvotes',
            old_name='parent',
            new_name='blog',
        ),
        migrations.RenameField(
            model_name='electvotes',
            old_name='parent',
            new_name='new',
        ),
        migrations.AlterField(
            model_name='electnew',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Создатель'),
        ),
        migrations.CreateModel(
            name='ElectNewComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField(blank=True)),
                ('is_edited', models.BooleanField(default=False, verbose_name='Изменено')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Удаено')),
                ('commenter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Комментатор')),
                ('new', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.electnew')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='elect_new_comment_replies', to='blog.electnewcomment', verbose_name='Родительский комментарий')),
            ],
            options={
                'verbose_name': 'комментарий к новости депутата',
                'verbose_name_plural': 'комментарии к новости депутата',
            },
        ),
        migrations.CreateModel(
            name='ElectCommentVotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(choices=[(-1, 'Не нравится'), (1, 'Нравится')], verbose_name='Голос')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.electnewcomment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.AddIndex(
            model_name='electnewcomment',
            index=django.contrib.postgres.indexes.BrinIndex(fields=['created'], name='blog_electn_created_c42832_brin'),
        ),
    ]
