from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from django.utils import timezone
from pilkit.processors import ResizeToFill, ResizeToFit, Transpose
from imagekit.models import ProcessedImageField
from django.db.models import Q
from ckeditor_uploader.fields import RichTextUploadingField
from users.helpers import upload_to_user_directory
from elect.models import Elect
from lists.models import ElectNewsCategory
from autoslug import AutoSlugField

"""
    Группируем все таблицы новостей здесь:
    1. Новости всего проекта,
    2. Лента депутата - его высказывания, выборы, работа с избирателями
"""


class Blog(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    image = ProcessedImageField(format='JPEG', blank=True, options={'quality': 90}, upload_to="blog/%Y/%m/%d/", processors=[ResizeToFit(width=1600, upscale=False)], verbose_name="Главное изображение")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Создан")
    description = models.CharField(max_length=500, blank=True, verbose_name="Описание")
    content = RichTextUploadingField(config_name='default',)
    comments_enabled = models.BooleanField(default=True, verbose_name="Разрешить комментарии")
    votes_on = models.BooleanField(default=True, verbose_name="Реакции разрешены")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name="Создатель")
    slug = AutoSlugField(populate_from='title', null=True)

    comment = models.PositiveIntegerField(default=0, verbose_name="Кол-во комментов")
    view = models.PositiveIntegerField(default=0, verbose_name="Кол-во просмотров")
    like = models.PositiveIntegerField(default=0, verbose_name="Кол-во лайков")
    dislike = models.PositiveIntegerField(default=0, verbose_name="Кол-во дизлайков")
    inert = models.PositiveIntegerField(default=0, verbose_name="Кол-во inert")
    repost = models.PositiveIntegerField(default=0, verbose_name="Кол-во репостов")

    class Meta:
        verbose_name = "Новость проекта"
        verbose_name_plural = "Новости проекта"
        indexes = (BrinIndex(fields=['created']),)
        ordering = ["-created"]

    def __str__(self):
        return self.title

    @classmethod
    def create_new(cls, creator, description, content, comments_enabled, votes_on, type):
        from notify.models import Notify

        blog = cls.objects.create(creator=creator,description=description,category=category,comments_enabled=comments_enabled,votes_on=votes_on)
        Notify.objects.create(creator_id=creator.pk, type="BLO", object_id=blog.pk, verb="ITE")
        return blog

    def likes(self):
        from common.model.votes import BlogVotes
        return BlogVotes.objects.filter(blog_id=self.pk, vote="LIK")
    def dislikes(self):
        from common.model.votes import BlogVotes
        return BlogVotes.objects.filter(blog_id=self.pk, vote="DIS")
    def inerts(self):
        from common.model.votes import BlogVotes
        return BlogVotes.objects.filter(blog_id=self.pk, vote="INE")

    def is_have_likes(self):
        return self.like > 0
    def is_have_dislikes(self):
        return self.dislike > 0
    def is_have_inerts(self):
        return self.inert > 0

    def is_suspended(self):
        return False
    def is_deleted(self):
        return False
    def is_closed(self):
        return False

    def likes_count(self):
        if self.like > 0:
            return self.like
        else:
            return ''
    def dislikes_count(self):
        if self.dislike > 0:
            return self.dislike
        else:
            return ''
    def inerts_count(self):
        if self.inert > 0:
            return self.inert
        else:
            return ''

    def count_comments(self):
        if self.comment > 0:
            return self.comment
        else:
            return ''

    def reposts_count(self):
        if self.repost > 0:
            return self.repost
        else:
            return ''

    def get_comments(self):
        from common.model.comments import BlogComment
        query = Q(blog_id=self.pk, parent__isnull=True)
        query.add(Q(Q(type="PUB")|Q(type="EDI")), Q.AND)
        return BlogComment.objects.filter(query)

    def get_created(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.created)

    def visits_count(self):
        return self.view

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return '/static/images/no_photo.jpg'

    def get_manager_tags(self):
        from tags.models import ManagerTag
        tags = ManagerTag.objects.filter(blog=self).values("name")
        return [i['name'] for i in tags]

    def count_views(self):
        return self.view

    def is_blog_in_bookmarks(self, user_id):
        from users.model.profile import Bookmarks
        return Bookmarks.objects.filter(blog=self, user_id=user_id).exists()

    def is_closed(self):
        return self.type == self.CLOSED

    def get_u_attach(self, user):
        from common.attach.elect_new_attach import get_u_blog_attach
        return get_u_blog_attach(self, user)

    def get_attach_photos(self):
        if "pho" in self.attach:
            query = []
            from gallery.models import Photo

            for item in self.attach.split(","):
                if item[:3] == "pho":
                    query.append(item[3:])
        return Photo.objects.filter(id__in=query)

    def get_attach_videos(self):
        if "vid" in self.attach:
            query = []
            from video.models import Video

            for item in self.attach.split(","):
                if item[:3] == "vid":
                    query.append(item[3:])
        return Video.objects.filter(id__in=query)

    def send_like(self, user, community):
        import json
        from common.model.votes import BlogVotes
        from django.http import HttpResponse
        if not self.votes_on:
            from django.http import Http404
            raise Http404
        try:
            item = BlogVotes.objects.get(blog=self, user=user)
            if item.vote == BlogVotes.DISLIKE:
                item.vote = BlogVotes.LIKE
                item.save(update_fields=['vote'])
                self.like += 1
                self.dislike -= 1
                self.save(update_fields=['like', 'dislike'])
            elif item.vote == BlogVotes.INERT:
                item.vote = BlogVotes.LIKE
                item.save(update_fields=['vote'])
                self.inert -= 1
                self.like += 1
                self.save(update_fields=['inert', 'like'])
            else:
                item.delete()
                self.like -= 1
                self.save(update_fields=['like'])
        except BlogVotes.DoesNotExist:
            BlogVotes.objects.create(blog=self, user=user, vote=BlogVotes.LIKE)
            self.like += 1
            self.save(update_fields=['like'])
            if community:
                from common.notify.notify import community_notify, community_wall
                community_notify(user, community, None, self.pk, "BLO", "c_blog_notify", "LIK")
                community_wall(user, community, None, self.pk, "BLO", "c_blog_notify", "LIK")
            else:
                from common.notify.notify import user_notify, user_wall
                user_notify(user, None, self.pk, "BLO", "u_blog_notify", "LIK")
                user_wall(user, None, self.pk, "BLO", "u_blog_notify", "LIK")
        return HttpResponse(json.dumps({"like_count": str(self.likes_count()),"dislike_count": str(self.dislikes_count()),"inert_count": str(self.inerts_count())}),content_type="application/json")

    def send_dislike(self, user, community):
        import json
        from common.model.votes import BlogVotes
        from django.http import HttpResponse
        if not self.votes_on:
            from django.http import Http404
            raise Http404
        try:
            item = BlogVotes.objects.get(blog=self, user=user)
            if item.vote == BlogVotes.LIKE:
                item.vote = BlogVotes.DISLIKE
                item.save(update_fields=['vote'])
                self.like -= 1
                self.dislike += 1
                self.save(update_fields=['like', 'dislike'])
            elif item.vote == BlogVotes.INERT:
                item.vote = BlogVotes.DISLIKE
                item.save(update_fields=['vote'])
                self.inert -= 1
                self.dislike += 1
                self.save(update_fields=['inert', 'dislike'])
            else:
                item.delete()
                self.dislike -= 1
                self.save(update_fields=['dislike'])
        except BlogVotes.DoesNotExist:
            BlogVotes.objects.create(blog=self, user=user, vote=BlogVotes.DISLIKE)
            self.dislike += 1
            self.save(update_fields=['dislike'])
            if community:
                from common.notify.notify import community_notify, community_wall
                community_notify(user, community, None, self.pk, "BLO", "c_blog_notify", "DIS")
                community_wall(user, community, None, self.pk, "BLO", "c_blog_notify", "DIS")
            else:
                from common.notify.notify import user_notify, user_wall
                user_notify(user, None, self.pk, "BLO", "u_blog_notify", "DIS")
                user_wall(user, None, self.pk, "BLO", "u_blog_notify", "DIS")
        return HttpResponse(json.dumps({"like_count": str(self.likes_count()),"dislike_count": str(self.dislikes_count()),"inert_count": str(self.inerts_count())}),content_type="application/json")

    def send_inert(self, user, community):
        import json
        from common.model.votes import BlogVotes
        from django.http import HttpResponse
        if not self.votes_on:
            from django.http import Http404
            raise Http404
        try:
            item = BlogVotes.objects.get(blog=self, user=user)
            if item.vote == BlogVotes.LIKE:
                item.vote = BlogVotes.INERT
                item.save(update_fields=['vote'])
                self.like -= 1
                self.inert += 1
                self.save(update_fields=['like', 'inert'])
            elif item.vote == BlogVotes.DISLIKE:
                item.vote = BlogVotes.INERT
                item.save(update_fields=['vote'])
                self.inert += 1
                self.dislike -= 1
                self.save(update_fields=['inert', 'dislike'])
            else:
                item.delete()
                self.inert -= 1
                self.save(update_fields=['inert'])
        except BlogVotes.DoesNotExist:
            BlogVotes.objects.create(blog=self, user=user, vote=BlogVotes.INERT)
            self.inert += 1
            self.save(update_fields=['inert'])
            if community:
                from common.notify.notify import community_notify, community_wall
                community_notify(user, community, None, self.pk, "BLO", "c_blog_notify", "INE")
                community_wall(user, community, None, self.pk, "BLO", "c_blog_notify", "INE")
            else:
                from common.notify.notify import user_notify, user_wall
                user_notify(user, None, self.pk, "BLO", "u_blog_notify", "INE")
                user_wall(user, None, self.pk, "BLO", "u_blog_notify", "INE")
        return HttpResponse(json.dumps({"like_count": str(self.likes_count()),"dislike_count": str(self.dislikes_count()),"inert_count": str(self.inerts_count())}),content_type="application/json")


class ElectNew(models.Model):
    PROCESSING, SUGGESTED, PUBLISHED, MANAGER, DELETED, CLOSED = '_PRO', 'SUG', 'PUB', 'MAN','_DEL','_CLO'
    DELETED_REJECTED, DELETED_SUGGESTED, CLOSED_SUGGESTED, DELETED_MANAGER, CLOSED_MANAGER, REJECTED = '_DELR','_DELS','_CLOS','_DELM','_CLOM','_REJ'
    TYPE = (
        (PROCESSING, 'обрабатывается'),(SUGGESTED, 'на рассмотрении'), (PUBLISHED, 'опубликована'),(DELETED, 'удалена'),(CLOSED, 'закрыта модератором'),(MANAGER, 'создана персоналом'),
        (DELETED_REJECTED, 'удалена отклоненная'),(DELETED_SUGGESTED, 'удалена предложенная'),(CLOSED_SUGGESTED, 'предложенная менеджерский'),(DELETED_MANAGER, 'удалена менеджерский'),(CLOSED_MANAGER, 'закрыта менеджерский'),(REJECTED, 'отклонена модератором')
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Создан")
    description = models.TextField(max_length=1000, blank=True, verbose_name="Описание")
    elect = models.ForeignKey(Elect, null=True, on_delete=models.SET_NULL, related_name="new_elect", verbose_name="Чиновник")
    category = models.ForeignKey(ElectNewsCategory, on_delete=models.SET_NULL, related_name="elect_cat", blank=True, null=True, verbose_name="Категория активности")
    type = models.CharField(choices=TYPE, default=PROCESSING, max_length=5, verbose_name="Статус записи")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="elect_new_creator", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Создатель")
    content = RichTextUploadingField(config_name='default',)
    comments_enabled = models.BooleanField(default=True, verbose_name="Разрешить комментарии")
    votes_on = models.BooleanField(default=True, verbose_name="Реакции разрешены")
    attach = models.CharField(blank=True, max_length=200, verbose_name="Прикрепленные элементы")
    image = ProcessedImageField(format='JPEG', blank=True, options={'quality': 90}, upload_to="blog/%Y/%m/%d/", processors=[ResizeToFit(width=1600, upscale=False)], verbose_name="Главное изображение")

    comment = models.PositiveIntegerField(default=0, verbose_name="Кол-во комментов")
    view = models.PositiveIntegerField(default=0, verbose_name="Кол-во просмотров")
    like = models.PositiveIntegerField(default=0, verbose_name="Кол-во лайков")
    dislike = models.PositiveIntegerField(default=0, verbose_name="Кол-во дизлайков")
    inert = models.PositiveIntegerField(default=0, verbose_name="Кол-во inert")
    repost = models.PositiveIntegerField(default=0, verbose_name="Кол-во репостов")

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Лента чиновника"
        indexes = (BrinIndex(fields=['created']),)
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def get_image(self):
        try:
            return self.elect.image.url
        except:
            return '/static/images/no_photo.jpg'

    def get_manager_tags(self):
        from tags.models import ManagerTag
        tags = ManagerTag.objects.filter(new=self).values("name")
        return [i['name'] for i in tags]

    def get_count_attach(self):
        if self.attach:
            length = self.attach.split(",")
            return "files_" + str(len(length))
        else:
            return "files_0"

    @classmethod
    def create_suggested_new(cls, creator, title, description, elect, attach, category):
        from elect.models import Elect
        try:
            _elect = Elect.objects.get(name=elect)
        except:
            _elect = None
        _attach = str(attach)
        _attach = _attach.replace("'", "").replace("[", "").replace("]", "").replace(" ", "")

        new = cls.objects.create(creator=creator,title=title,description=description,elect=_elect,attach=_attach,category=category,type=ElectNew.SUGGESTED,)
        return new

    def edit_new(self, title, description, elect, attach, category):
        from elect.models import Elect
        _attach = str(attach)
        _attach = _attach.replace("'", "").replace("[", "").replace("]", "").replace(" ", "")
        try:
            _elect = Elect.objects.get(name=elect)
        except Elect.DoesNotExist:
            _elect = None
        self.title = title
        self.description = description
        self.elect = _elect
        self.attach = _attach
        self.category = category
        self.save()
        return self

    def make_publish_new(self, title, description, elect, attach, category, tags, manager_id):
        from elect.models import Elect
        from notify.models import Notify, Wall
        from common.notify.progs import user_send_notify, user_send_wall
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        from logs.model.manage_elect_new import ElectNewManageLog

        _attach = str(attach)
        _attach = _attach.replace("'", "").replace("[", "").replace("]", "").replace(" ", "")

        # экранируем проблемы с получением депутата. Он должен быть точно, но в БД мы прописали null=True,
        # так как мы не хотим, чтобы при удалении депутата связанные с ним активности также удалились.
        try:
            _elect = Elect.objects.get(name=elect)
        except Elect.DoesNotExist:
            _elect = Elect.objects.get(pk=94)

        self.type = ElectNew.PUBLISHED
        self.title = title
        self.description = description
        self.elect = elect
        self.attach = _attach
        self.category = category
        self.save()

        # создаем запись для стены и отсылаем сокет для отрисовки в реале
        Wall.objects.create(creator_id=manager_id, type="ELN", object_id=self.pk, verb="ITE")
        user_send_wall(self.pk, None, "elect_new_wall")

        # создаем уведы для каждого. кто подписан на депутата активности.
        for user_id in self.elect.get_subscribers_ids():
            Notify.objects.create(creator_id=manager_id, recipient_id=user_id, type="ELN", object_id=self.pk, verb="ITE")
            user_send_notify(self.pk, self.creator.pk, user_id, None, "elect_new_notify")

        # отправляем увед создателю активности, что ее успешно опубликовали
        Notify.objects.create(creator_id=manager_id, recipient_id=self.creator.pk, type="ELN", object_id=self.pk, verb="ELNC")
        ElectNewManageLog.objects.create(item=self.pk, manager=manager_id, action_type=ElectNewManageLog.ITEM_PUBLISHED)
        channel_layer = get_channel_layer()
        payload = {
            'type': 'receive',
            'key': 'notification',
            'id': str(self.pk),
            'recipient_id': str(self.creator.pk),
            'name': "elect_new_published",
        }
        async_to_sync(channel_layer.group_send)('notification', payload)

        # плюсуем единичку создателю к его кол-ву созданных активностей. Добавляем теги с формы.
        self.creator.plus_elect_news(1)
        if tags:
            from tags.models import ManagerTag
            for _tag in tags:
                tag = ManagerTag.objects.get(pk=_tag)
                tag.new.add(self)
        return self

    def is_published(self):
        return self.type == ElectNew.PUBLISHED
    def is_manager(self):
        return self.type == ElectNew.MANAGER
    def is_suggested(self):
        return self.type == ElectNew.SUGGESTED
    def is_deleted(self):
        return self.type[:4] == "_DEL"
    def is_rejected(self):
        return self.type == ElectNew.REJECTED
    def is_closed(self):
        return self.type[:4] == "_CLO"
    def is_suspended(self):
        return False

    def likes(self):
        from common.model.votes import ElectNewVotes2
        return ElectNewVotes2.objects.filter(new_id=self.pk, vote="LIK")
    def dislikes(self):
        from common.model.votes import ElectNewVotes2
        return ElectNewVotes2.objects.filter(new_id=self.pk, vote="DIS")
    def inerts(self):
        from common.model.votes import ElectNewVotes2
        return ElectNewVotes2.objects.filter(new_id=self.pk, vote="INE")

    def count_views(self):
        return self.view

    def is_have_likes(self):
        return self.like > 0
    def is_have_dislikes(self):
        return self.dislike > 0
    def is_have_inerts(self):
        return self.inert > 0

    def likes_count(self):
        if self.like > 0:
            return self.like
        else:
            return ''
    def dislikes_count(self):
        if self.dislike > 0:
            return self.dislike
        else:
            return ''
    def inerts_count(self):
        if self.inert > 0:
            return self.inert
        else:
            return ''

    def reposts_count(self):
        if self.repost > 0:
            return self.repost
        else:
            return ''

    def get_created(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.created)

    def visits_count(self):
        return self.view

    def get_image_url(self):
        return self.creator.s_avatar.url

    def count_comments(self):
        if self.comment > 0:
            return self.comment
        else:
            return ''

    def get_comments(self):
        from common.model.comments import ElectNewComment
        query = Q(new_id=self.pk, parent__isnull=True)
        query.add(Q(Q(type="PUB")|Q(type="EDI")), Q.AND)
        return ElectNewComment.objects.filter(query)

    def get_u_attach(self, user):
        from common.attach.elect_new_attach import get_u_elect_new_attach
        return get_u_elect_new_attach(self, user)

    def get_attach_photos(self):
        if "pho" in self.attach:
            query = []
            from gallery.models import Photo

            for item in self.attach.split(","):
                if item[:3] == "pho":
                    query.append(item[3:])
        return Photo.objects.filter(id__in=query)

    def get_attach_videos(self):
        if "vid" in self.attach:
            query = []
            from video.models import Video

            for item in self.attach.split(","):
                if item[:3] == "vid":
                    query.append(item[3:])
        return Video.objects.filter(id__in=query)

    def send_like(self, user, community):
        import json
        from common.model.votes import ElectNewVotes2
        from django.http import HttpResponse
        if not self.votes_on:
            from django.http import Http404
            raise Http404
        try:
            item = ElectNewVotes2.objects.get(new=self, user=user)
            if item.vote == ElectNewVotes2.DISLIKE:
                item.vote = ElectNewVotes2.LIKE
                item.save(update_fields=['vote'])
                self.like += 1
                if self.dislike > 0:
                    self.dislike -= 1
                self.save(update_fields=['like', 'dislike'])
                if self.elect:
                    elect = self.elect
                    elect.like += 1
                    if elect.dislike > 0:
                        elect.dislike -= 1
                    elect.save(update_fields=['like', 'dislike'])
            elif item.vote == ElectNewVotes2.INERT:
                item.vote = ElectNewVotes2.LIKE
                item.save(update_fields=['vote'])
                self.inert -= 1
                self.like += 1
                self.save(update_fields=['inert', 'like'])
                if self.elect:
                    elect = self.elect
                    elect.inert -= 1
                    elect.like += 1
                    elect.save(update_fields=['inert', 'like'])
            else:
                item.delete()
                self.like -= 1
                self.save(update_fields=['like'])
                if self.elect:
                    elect = self.elect
                    elect.like -= 1
                    elect.save(update_fields=['like'])
        except ElectNewVotes2.DoesNotExist:
            ElectNewVotes2.objects.create(new=self, user=user, vote=ElectNewVotes2.LIKE)
            self.like += 1
            self.save(update_fields=['like'])
            if self.elect:
                elect = self.elect
                elect.like += 1
                elect.save(update_fields=['like'])
            if community:
                from common.notify.notify import community_notify, community_wall
                community_notify(user, community, None, self.pk, "ELN", "u_elect_new_notify", "LIK")
                community_wall(user, community, None, self.pk, "ELN", "u_elect_new_notify", "LIK")
            else:
                from common.notify.notify import user_notify, user_wall
                user_notify(user, None, self.pk, "ELN", "u_elect_new_notify", "LIK")
                user_wall(user, None, self.pk, "ELN", "u_elect_new_notify", "LIK")
        return HttpResponse(json.dumps({"like_count": str(self.likes_count()),"dislike_count": str(self.dislikes_count()),"inert_count": str(self.inerts_count())}),content_type="application/json")

    def send_dislike(self, user, community):
        import json
        from common.model.votes import ElectNewVotes2
        from django.http import HttpResponse
        if not self.votes_on:
            from django.http import Http404
            raise Http404
        try:
            item = ElectNewVotes2.objects.get(new=self, user=user)
            if item.vote == ElectNewVotes2.LIKE:
                item.vote = ElectNewVotes2.DISLIKE
                item.save(update_fields=['vote'])
                self.like -= 1
                self.dislike += 1
                self.save(update_fields=['like', 'dislike'])
                if self.elect:
                    elect = self.elect
                    elect.like -= 1
                    elect.dislike += 1
                    elect.save(update_fields=['like', 'dislike'])
            elif item.vote == ElectNewVotes2.INERT:
                item.vote = ElectNewVotes2.DISLIKE
                item.save(update_fields=['vote'])
                self.inert -= 1
                self.dislike += 1
                self.save(update_fields=['inert', 'dislike'])
                if self.elect:
                    elect = self.elect
                    elect.inert -= 1
                    elect.dislike += 1
                    elect.save(update_fields=['inert', 'dislike'])
            else:
                item.delete()
                self.dislike -= 1
                self.save(update_fields=['dislike'])
                if self.elect:
                    elect = self.elect
                    elect.dislike -= 1
                    elect.save(update_fields=['dislike'])
        except ElectNewVotes2.DoesNotExist:
            ElectNewVotes2.objects.create(new=self, user=user, vote=ElectNewVotes2.DISLIKE)
            self.dislike += 1
            self.save(update_fields=['dislike'])
            if self.elect:
                elect = self.elect
                elect.dislike += 1
                elect.save(update_fields=['dislike'])
            if community:
                from common.notify.notify import community_notify, community_wall
                community_notify(user, community, None, self.pk, "ELN", "u_elect_new_notify", "DIS")
                community_wall(user, community, None, self.pk, "ELN", "u_elect_new_notify", "DIS")
            else:
                from common.notify.notify import user_notify, user_wall
                user_notify(user, None, self.pk, "ELN", "u_elect_new_notify", "DIS")
                user_wall(user, None, self.pk, "ELN", "u_elect_new_notify", "DIS")
        return HttpResponse(json.dumps({"like_count": str(self.likes_count()),"dislike_count": str(self.dislikes_count()),"inert_count": str(self.inerts_count())}),content_type="application/json")

    def send_inert(self, user, community):
        import json
        from common.model.votes import ElectNewVotes2
        from django.http import HttpResponse
        if not self.votes_on:
            from django.http import Http404
            raise Http404
        try:
            item = ElectNewVotes2.objects.get(new=self, user=user)
            if item.vote == ElectNewVotes2.LIKE:
                item.vote = ElectNewVotes2.INERT
                item.save(update_fields=['vote'])
                self.like -= 1
                self.inert += 1
                self.save(update_fields=['like', 'inert'])
                if self.elect:
                    elect = self.elect
                    elect.like -= 1
                    elect.inert += 1
                    elect.save(update_fields=['like', 'inert'])
            elif item.vote == ElectNewVotes2.DISLIKE:
                item.vote = ElectNewVotes2.INERT
                item.save(update_fields=['vote'])
                self.inert += 1
                self.dislike -= 1
                self.save(update_fields=['inert', 'dislike'])
                if self.elect:
                    elect = self.elect
                    elect.inert += 1
                    elect.dislike -= 1
                    elect.save(update_fields=['inert', 'dislike'])
            else:
                item.delete()
                self.inert -= 1
                self.save(update_fields=['inert'])
                if self.elect:
                    elect = self.elect
                    elect.inert -= 1
                    elect.save(update_fields=['inert'])
        except ElectNewVotes2.DoesNotExist:
            ElectNewVotes2.objects.create(new=self, user=user, vote=ElectNewVotes2.INERT)
            self.inert += 1
            self.save(update_fields=['inert'])
            if self.elect:
                elect = self.elect
                elect.inert += 1
                elect.save(update_fields=['inert'])
            if community:
                from common.notify.notify import community_notify, community_wall
                community_notify(user, community, None, self.pk, "ELN", "u_elect_new_notify", "INE")
                community_wall(user, community, None, self.pk, "ELN", "u_elect_new_notify", "INE")
            else:
                from common.notify.notify import user_notify, user_wall
                user_notify(user, None, self.pk, "ELN", "u_elect_new_notify", "INE")
                user_wall(user, None, self.pk, "ELN", "u_elect_new_notify", "INE")
        return HttpResponse(json.dumps({"like_count": str(self.likes_count()),"dislike_count": str(self.dislikes_count()),"inert_count": str(self.inerts_count())}),content_type="application/json")

    def delete_item(self):
        from notify.models import Notify, Wall
        if self.type == "PUB":
            self.type = ElectNew.DELETED
        elif self.type == "SUG":
            self.type = ElectNew.DELETED_SUGGESTED
        elif self.type == "MAN":
            self.type = ElectNew.DELETED_MANAGER
        elif self.type == "_REJ":
            self.type = ElectNew.DELETED_REJECTED
        self.save(update_fields=['type'])
        if Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="C")
        if Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="C")
    def restore_item(self):
        from notify.models import Notify, Wall
        if self.type == "_DEL":
            self.type = ElectNew.PUBLISHED
        elif self.type == "_DELS":
            self.type = ElectNew.SUGGESTED
        elif self.type == "_DELM":
            self.type = ElectNew.MANAGER
        elif self.type == "_DELR":
            self.type = ElectNew.REJECTED
        self.save(update_fields=['type'])
        if Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="R")
        if Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="R")

    def close_item(self):
        from notify.models import Notify, Wall
        if self.type == "PUB":
            self.type = ElectNew.CLOSED
        elif self.type == "PRI":
            self.type = ElectNew.CLOSED_PRIVATE
        elif self.type == "MAN":
            self.type = ElectNew.CLOSED_MANAGER
        self.save(update_fields=['type'])
        if Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="C")
        if Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="C")
    def abort_close_item(self):
        from notify.models import Notify, Wall
        if self.type == "_CLO":
            self.type = ElectNew.PUBLISHED
        elif self.type == "_CLOP":
            self.type = ElectNew.PRIVATE
        elif self.type == "_CLOM":
            self.type = ElectNew.MANAGER
        self.save(update_fields=['type'])
        if Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Notify.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="R")
        if Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").exists():
            Wall.objects.filter(type="ELN", object_id=self.pk, verb="ITE").update(status="R")

    def get_edit_attach(self, user):
        from common.attach.elect_new_attach import get_elect_new_edit
        return get_elect_new_edit(self, user)
