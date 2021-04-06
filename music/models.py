import uuid
from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import BrinIndex
from django.utils import timezone
from pilkit.processors import ResizeToFill, ResizeToFit
from imagekit.models import ProcessedImageField
from users.helpers import upload_to_user_directory
from pilkit.processors import ResizeToFill, ResizeToFit, Transpose
from imagekit.models import ProcessedImageField
from django.db.models import Q


class SoundList(models.Model):
    MAIN = 'MAI'
    LIST = 'LIS'
    DELETED = 'DEL'
    PRIVATE = 'PRI'
    CLOSED = 'CLO'
    MANAGER = 'MAN'
    TYPE = (
        (MAIN, 'Основной'),
        (LIST, 'Пользовательский'),
        (DELETED, 'Удалённый'),
        (PRIVATE, 'Приватный'),
        (CLOSED, 'Закрытый менеджером'),
        (MANAGER, 'Созданный персоналом'),
    )
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_playlist', db_index=False, on_delete=models.CASCADE, verbose_name="Создатель")
    type = models.CharField(max_length=5, choices=TYPE, default=LIST, verbose_name="Тип")
    order = models.PositiveIntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, verbose_name="uuid")
    image = ProcessedImageField(format='JPEG', blank=True, options={'quality': 100}, upload_to=upload_to_user_directory, processors=[Transpose(), ResizeToFit(width=400, height=400)])

    users = models.ManyToManyField("users.User", blank=True, related_name='user_soundlist')

    def __str__(self):
        return self.name + " " + self.creator.get_full_name()

    def is_track_in_list(self, track_id):
        return self.playlist.filter(pk=track_id).values("pk").exists()

    def is_not_empty(self):
        return self.playlist.filter(list=self).values("pk").exists()

    def get_my_playlist(self):
        query = Q(type="PUB") & Q(type="PRI")
        return self.playlist.filter(query)

    def get_playlist(self):
        query = Q(type="PUB")
        queryset = self.playlist.filter(query)
        return queryset

    def get_users_ids(self):
        users = self.users.exclude(perm="DE").exclude(perm="BL").exclude(perm="PV").values("pk")
        return [i['pk'] for i in users]

    def is_user_can_add_list(self, user_id):
        if self.creator.pk != user_id and user_id not in self.get_users_ids():
            return True
        else:
            return False
    def is_user_can_delete_list(self, user_id):
        if self.creator.pk != user_id and user_id in self.get_users_ids():
            return True
        else:
            return False

    def get_remote_image(self, image_url):
        import os
        from django.core.files import File
        from urllib import request

        result = request.urlretrieve(image_url)
        self.image.save(
            os.path.basename(image_url),
            File(open(result[0], 'rb'))
        )
        self.save()

    def count_tracks(self):
        query = Q(type="MAI") | Q(type="LIS")
        return self.playlist.filter(query).values("pk").count()

    def is_main_list(self):
        return self.type == self.MAIN
    def is_user_list(self):
        return self.type == self.LIST

    class Meta:
        verbose_name = "список треков"
        verbose_name_plural = "списки треков"
        ordering = ['order']


class Music(models.Model):
    PROCESSING = 'PRO'
    PUBLISHED = 'PUB'
    DELETED = 'DEL'
    PRIVATE = 'PRI'
    CLOSED = 'CLO'
    MANAGER = 'MAN'
    TYPE = (
        (PROCESSING, 'Обработка'),
        (PUBLISHED, 'Опубликовано'),
        (DELETED, 'Удалено'),
        (PRIVATE, 'Приватно'),
        (CLOSED, 'Закрыто модератором'),
        (MANAGER, 'Созданный персоналом'),
    )
    artwork_url = ProcessedImageField(format='JPEG', blank=True, options={'quality': 100}, upload_to=upload_to_user_directory, processors=[Transpose(), ResizeToFit(width=100, height=100)])
    created = models.DateTimeField(default=timezone.now)
    duration = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)
    release_year = models.CharField(max_length=10, blank=True, null=True)
    list = models.ManyToManyField(SoundList, related_name='playlist', blank="True")
    type = models.CharField(max_length=5, choices=TYPE, default=PROCESSING, verbose_name="Тип")

    def __str__(self):
        return self.title

    def get_mp3(self):
        url = self.uri + '/stream?client_id=3ddce5652caa1b66331903493735ddd64d'
        url.replace("\\?", "%3f")
        url.replace("=", "%3d")
        return url

    def get_remote_image(self, image_url):
        import os
        from django.core.files import File
        from urllib import request

        result = request.urlretrieve(image_url)
        self.artwork_url.save(
            os.path.basename(image_url),
            File(open(result[0], 'rb'))
        )
        self.save()

    class Meta:
        verbose_name = "треки"
        verbose_name_plural = "треки"
        indexes = (BrinIndex(fields=['created']),)
        ordering = ['-created']
