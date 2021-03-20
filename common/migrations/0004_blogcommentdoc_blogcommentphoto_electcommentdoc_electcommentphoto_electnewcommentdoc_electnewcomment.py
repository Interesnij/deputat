# Generated by Django 3.1.5 on 2021-02-26 16:55

from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields
import users.helpers


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_blogcommentvotes_blogvotes_electcommentvotes_electnewcommentvotes_electnewvotes2'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElectNewCommentPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', imagekit.models.fields.ProcessedImageField(upload_to=users.helpers.upload_to_user_directory)),
                ('comment', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='elect_new_comment_photo', to='common.electnewcomment')),
            ],
            options={
                'verbose_name': 'Фото коммента к новости депутата',
                'verbose_name_plural': 'Фото коммента к новости депутата',
            },
        ),
        migrations.CreateModel(
            name='ElectNewCommentDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=users.helpers.upload_to_user_directory, verbose_name='Документ')),
                ('comment', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='elect_new_comment_doc', to='common.electnewcomment')),
            ],
            options={
                'verbose_name': 'Документ коммента к новости депутата',
                'verbose_name_plural': 'Документы коммента к новости депутата',
            },
        ),
        migrations.CreateModel(
            name='ElectCommentPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', imagekit.models.fields.ProcessedImageField(upload_to=users.helpers.upload_to_user_directory)),
                ('comment', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='elect_comment_photo', to='common.electnewcomment')),
            ],
            options={
                'verbose_name': 'Фото коммента к отзыву о депутате',
                'verbose_name_plural': 'Фото коммента к отзыву о депутате',
            },
        ),
        migrations.CreateModel(
            name='ElectCommentDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=users.helpers.upload_to_user_directory, verbose_name='Документ')),
                ('comment', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='elect_comment_doc', to='common.electnewcomment')),
            ],
            options={
                'verbose_name': 'Документ коммента к отзыву о депутате',
                'verbose_name_plural': 'Документы коммента к отзыву о депутате',
            },
        ),
        migrations.CreateModel(
            name='BlogCommentPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', imagekit.models.fields.ProcessedImageField(upload_to=users.helpers.upload_to_user_directory)),
                ('comment', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='blog_comment_image', to='common.blogcomment')),
            ],
            options={
                'verbose_name': 'Фото коммента к статье блога',
                'verbose_name_plural': 'Фото коммента к статье блога',
            },
        ),
        migrations.CreateModel(
            name='BlogCommentDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=users.helpers.upload_to_user_directory, verbose_name='Документ')),
                ('comment', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='blog_comment_doc', to='common.blogcomment')),
            ],
            options={
                'verbose_name': 'Документ коммента к статье блога',
                'verbose_name_plural': 'Документы коммента к статье блога',
            },
        ),
    ]
