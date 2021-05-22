from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import BrinIndex
from blog.models import Blog, ElectNew
from django.db.models import Q


"""
    Группируем все таблицы комментов здесь:
    1. Комменты блога проекта,
    2. Комменты новостей чиновника
"""

class BlogComment(models.Model):
    EDITED, PUBLISHED, PROCESSING = 'EDI', 'PUB', '_PRO'
    DELETED, EDITED_DELETED = '_DEL', '_DELE'
    CLOSED, EDITED_CLOSED = '_CLO', '_CLOE'
    STATUS = (
        (PUBLISHED, 'Опубликовано'),(EDITED, 'Изменённый'),(PROCESSING, 'Обработка'),
        (DELETED, 'Удалённый'), (DELETED, 'Удалённый изменённый'),
        (CLOSED, 'Закрытый менеджером'), (CLOSED, 'Закрытый изменённый'),
    )
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='blog_comment_replies', null=True, blank=True, verbose_name="Родительский комментарий")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Создан")
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Комментатор")
    text = models.TextField(blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, blank=True, null=True)
    attach = models.CharField(blank=True, max_length=200, verbose_name="Прикрепленные элементы")
    status = models.CharField(max_length=5, choices=STATUS, default=PROCESSING, verbose_name="Тип комментария")
    like = models.PositiveIntegerField(default=0, verbose_name="Кол-во лайков")

    class Meta:
        indexes = (BrinIndex(fields=['created']), )
        verbose_name = "комментарий к статье"
        verbose_name_plural = "комментарии к статье"
        ordering = ["-created"]

    def __str__(self):
        if self.text:
            return self.text[:10]
        else:
            return 'Комментатор ' + str(self.commenter)

    def get_created(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.created)

    def get_replies(self):
        return self.blog_comment_replies.filter(Q(status="PUB")|Q(status="EDI"))

    def count_replies(self):
        return self.get_replies().values("pk").count()

    def likes(self):
        from common.model.votes import BlogCommentVotes
        return BlogCommentVotes.objects.filter(comment_id=self.pk, vote__gt=0)

    def likes_count(self):
        if self.like > 0:
            return self.like
        else:
            return ''

    @classmethod
    def create_comment(cls, commenter, attach, blog, parent, text):
        from common.notify.notify import user_comment_notify, user_comment_wall
        from common.processing import get_blog_comment_processing

        _attach = str(attach)
        _attach = _attach.replace("'", "").replace("[", "").replace("]", "").replace(" ", "")
        comment = BlogComment.objects.create(commenter=commenter, attach=_attach, parent=parent, blog=blog, text=text)
        blog.comment += 1
        blog.save(update_fields=["comment"])
        commenter.plus_comments(1)
        get_blog_comment_processing(comment)
        if comment.parent:
            user_comment_notify(comment.commenter, comment.pk, "BLOC", "u_blog_comment_notify", "REP")
            user_comment_wall(comment.commenter, comment.pk, "BLOC", "u_blog_comment_notify", "REP")
        else:
            user_comment_notify(comment.commenter, comment.pk, "BLOC", "u_blog_comment_notify", "COM")
            user_comment_wall(comment.commenter, comment.pk, "BLOC", "u_blog_comment_notify", "COM")
        return comment

    def count_replies_ru(self):
        count = self.get_replies().count()
        a = count % 10
        b = count % 100
        if (a == 1) and (b != 11):
            return str(count) + " ответ"
        elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
            return str(count) + " ответа"
        else:
            return str(count) + " ответов"

    def get_u_attach(self, user):
        from common.attach.comment_attach import get_u_blog_comment_attach
        return get_u_blog_comment_attach(self, user)

    def get_attach_photos(self):
        if "pho" in self.attach:
            query = []
            from gallery.models import Photo

            for item in self.attach.split(","):
                if item[:3] == "pho":
                    query.append(item[3:])
        return Photo.objects.filter(id__in=query)

    def get_attach_videos(self):
        if "pho" in self.attach:
            query = []
            from video.models import Video

            for item in self.attach.split(","):
                if item[:3] == "vid":
                    query.append(item[3:])
        return Video.objects.filter(id__in=query)

    def delete_comment(self):
        from notify.models import Notify, Wall
        if self.status == "PUB":
            self.status = BlogComment.DELETED
        elif self.status == "EDI":
            self.status = BlogComment.DELETED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.blog.comment -= 1
            self.parent.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").update(status="C")
        else:
            self.blog.comment -= 1
            self.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").update(status="C")
        if Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").update(status="C")
    def restore_comment(self):
        from notify.models import Notify, Wall
        if self.status == "_DEL":
            self.status = BlogComment.PUBLISHED
        elif self.status == "_DELE":
            self.status = BlogComment.EDITED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.blog.comment += 1
            self.parent.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").update(status="R")
        else:
            self.blog.comment += 1
            self.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").update(status="R")
        if Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").update(status="R")

    def close_item(self):
        from notify.models import Notify, Wall
        if self.status == "PUB":
            self.status = BlogComment.CLOSED
        elif self.status == "EDI":
            self.status = BlogComment.EDITED_CLOSED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.blog.comment -= 1
            self.parent.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").update(status="C")
        else:
            self.blog.comment -= 1
            self.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").update(status="C")
        if Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").update(status="C")
    def abort_close_item(self):
        from notify.models import Notify, Wall
        if self.status == "_CLO":
            self.status = BlogComment.PUBLISHED
        elif self.status == "_CLOE":
            self.status = BlogComment.EDITED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.blog.comment += 1
            self.parent.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="REP").update(status="R")
        else:
            self.blog.comment += 1
            self.blog.save(update_fields=["comment"])
            if Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="BLOC", object_id=self.pk, verb__contains="COM").update(status="R")
        if Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="BLOC", object_id=self.pk, verb="COM").update(status="R")

    def send_like(self, user, community):
        import json
        from common.model.votes import BlogCommentVotes
        from django.http import HttpResponse
        from common.notify.notify import user_notify, user_wall
        try:
            item = BlogCommentVotes.objects.get(comment=self, user=user)
            if item.vote != BlogCommentVotes.LIKE:
                item.vote = BlogCommentVotes.LIKE
                item.save(update_fields=['vote'])
                self.like += 1
                self.dislike -= 1
                self.save(update_fields=['like', 'dislike'])
            else:
                item.delete()
                self.like -= 1
                self.save(update_fields=['like'])
        except BlogCommentVotes.DoesNotExist:
            BlogCommentVotes.objects.create(comment=self, user=user, vote=BlogCommentVotes.LIKE)
            self.like += 1
            self.save(update_fields=['like'])
            if self.parent:
                if community:
                    from common.notify.notify import community_notify, community_wall
                    community_notify(user, community, None, self.pk, "BLOC", "u_blog_comment_notify", "LRE")
                    community_wall(user, community, None, self.pk, "BLOC", "u_blog_comment_notify", "LCO")
                else:
                    from common.notify.notify import user_notify, user_wall
                    user_notify(user, None, self.pk, "BLOC", "u_blog_comment_notify", "LRE")
                    user_wall(user, None, self.pk, "BLOC", "u_blog_comment_notify", "LCO")
            else:
                if community:
                    from common.notify.notify import community_notify, community_wall
                    community_notify(user, community, None, self.pk, "PHOC", "u_blog_comment_notify", "LCO")
                    community_wall(user, community, None, self.pk, "PHOC", "u_blog_comment_notify", "LCO")
                else:
                    from common.notify.notify import user_notify, user_wall
                    user_notify(user, None, self.pk, "BLOC", "u_blog_comment_notify", "LCO")
                    user_wall(user, None, self.pk, "BLOC", "u_blog_comment_notify", "LCO")
        return HttpResponse(json.dumps({"like_count": str(self.like)}),content_type="application/json")



class ElectNewComment(models.Model):
    EDITED, PUBLISHED, PROCESSING = 'EDI', 'PUB', '_PRO'
    DELETED, EDITED_DELETED = '_DEL', '_DELE'
    CLOSED, EDITED_CLOSED = '_CLO', '_CLOE'
    STATUS = (
        (PUBLISHED, 'Опубликовано'),(EDITED, 'Изменённый'),(PROCESSING, 'Обработка'),
        (DELETED, 'Удалённый'), (DELETED, 'Удалённый изменённый'),
        (CLOSED, 'Закрытый менеджером'), (CLOSED, 'Закрытый изменённый'),
    )
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='elect_new_comment_replies', null=True, blank=True, verbose_name="Родительский комментарий")
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name="Создан")
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Комментатор")
    text = models.TextField(blank=True)
    new = models.ForeignKey(ElectNew, on_delete=models.CASCADE, blank=True, null=True)
    attach = models.CharField(blank=True, max_length=200, verbose_name="Прикрепленные элементы")
    status = models.CharField(max_length=5, choices=STATUS, default=PROCESSING, verbose_name="Тип комментария")
    like = models.PositiveIntegerField(default=0, verbose_name="Кол-во лайков")

    class Meta:
        indexes = (BrinIndex(fields=['created']), )
        verbose_name = "комментарий к новости депутата"
        verbose_name_plural = "комментарии к новости депутата"
        ordering = ["-created"]

    def __str__(self):
        return "{0}/{1}".format(self.commenter.get_full_name(), self.text[:10])

    def get_created(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.created)

    def get_replies(self):
        return self.elect_new_comment_replies.filter(Q(status="PUB")|Q(status="EDI"))

    def count_replies(self):
        return self.get_replies().values("pk").count()

    def likes(self):
        from common.model.votes import ElectNewCommentVotes
        return ElectNewCommentVotes.objects.filter(comment_id=self.pk, vote__gt=0)

    def likes_count(self):
        if self.like > 0:
            return self.like
        else:
            return ''

    @classmethod
    def create_comment(cls, commenter, attach, new, parent, text):
        from common.notify.notify import user_comment_notify, user_comment_wall
        from common.processing import get_elect_new_comment_processing

        _attach = str(attach)
        _attach = _attach.replace("'", "").replace("[", "").replace("]", "").replace(" ", "")
        comment = ElectNewComment.objects.create(commenter=commenter, attach=_attach, parent=parent, new=new, text=text)
        new.comment += 1
        new.save(update_fields=["comment"])
        commenter.plus_comments(1)
        if comment.parent:
            user_comment_notify(comment.commenter, comment.pk, "ELNC", "u_elect_new_comment_notify", "REP")
            user_comment_wall(comment.commenter, comment.pk, "ELNC", "u_elect_new_comment_notify", "REP")
        else:
            user_comment_notify(comment.commenter, comment.pk, "ELNC", "u_elect_new_comment_notify", "COM")
            user_comment_wall(comment.commenter, comment.pk, "ELNC", "u_elect_new_comment_notify", "COM")
        get_elect_new_comment_processing(comment)
        return comment

    def count_replies_ru(self):
        count = self.get_replies().count()
        a = count % 10
        b = count % 100
        if (a == 1) and (b != 11):
            return str(count) + " ответ"
        elif (a >= 2) and (a <= 4) and ((b < 10) or (b >= 20)):
            return str(count) + " ответа"
        else:
            return str(count) + " ответов"

    def get_u_attach(self, user):
        from common.attach.comment_attach import get_u_elect_new_comment_attach
        return get_u_elect_new_comment_attach(self, user)

    def get_attach_photos(self):
        if "pho" in self.attach:
            query = []
            from gallery.models import Photo

            for item in self.attach.split(","):
                if item[:3] == "pho":
                    query.append(item[3:])
        return Photo.objects.filter(id__in=query)

    def get_attach_videos(self):
        if "pho" in self.attach:
            query = []
            from video.models import Video

            for item in self.attach.split(","):
                if item[:3] == "vid":
                    query.append(item[3:])
        return Video.objects.filter(id__in=query)

    def delete_comment(self):
        from notify.models import Notify, Wall
        if self.status == "PUB":
            self.status = ElectNewComment.DELETED
        elif self.status == "EDI":
            self.status = ElectNewComment.DELETED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.new.comment -= 1
            self.parent.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="REP").update(status="C")
        else:
            self.new.comment -= 1
            self.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").update(status="C")
        if Wall.objects.filter(type="PHOC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="PHOC", object_id=self.pk, verb="COM").update(status="C")
    def restore_comment(self):
        from notify.models import Notify, Wall
        if self.status == "_DEL":
            self.status = ElectNewComment.PUBLISHED
        elif self.status == "_DELE":
            self.status = ElectNewComment.EDITED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.new.comment += 1
            self.parent.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="REP").update(status="R")
        else:
            self.new.comment += 1
            self.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").update(status="R")
        if Wall.objects.filter(type="ELNC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="ELNC", object_id=self.pk, verb="COM").update(status="R")

    def close_item(self):
        from notify.models import Notify, Wall
        if self.status == "PUB":
            self.status = ElectNewComment.CLOSED
        elif self.status == "EDI":
            self.status = ElectNewComment.EDITED_CLOSED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.new.comment -= 1
            self.parent.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="REP").update(status="C")
        else:
            self.new.comment -= 1
            self.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").update(status="C")
        if Wall.objects.filter(type="ELNC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="ELNC", object_id=self.pk, verb="COM").update(status="C")
    def abort_close_item(self):
        from notify.models import Notify, Wall
        if self.status == "_CLO":
            self.status = ElectNewComment.PUBLISHED
        elif self.status == "_CLOE":
            self.status = ElectNewComment.EDITED
        self.save(update_fields=['status'])
        if self.parent:
            self.parent.new.comment += 1
            self.parent.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="PHOC", object_id=self.pk, verb__contains="REP").exists():
                Notify.objects.filter(type="PHOC", object_id=self.pk, verb__contains="REP").update(status="R")
        else:
            self.new.comment += 1
            self.new.save(update_fields=["comment"])
            if Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").exists():
                Notify.objects.filter(type="ELNC", object_id=self.pk, verb__contains="COM").update(status="R")
        if Wall.objects.filter(type="ELNC", object_id=self.pk, verb="COM").exists():
            Wall.objects.filter(type="ELNC", object_id=self.pk, verb="COM").update(status="R")

    def send_like(self, user, community):
        import json
        from common.model.votes import ElectNewCommentVotes
        from django.http import HttpResponse
        from common.notify.notify import user_notify, user_wall
        try:
            item = ElectNewCommentVotes.objects.get(comment=self, user=user)
            if item.vote != ElectNewCommentVotes.LIKE:
                item.vote = ElectNewCommentVotes.LIKE
                item.save(update_fields=['vote'])
                self.like += 1
                self.dislike -= 1
                self.save(update_fields=['like', 'dislike'])
            else:
                item.delete()
                self.like -= 1
                self.save(update_fields=['like'])
        except ElectNewCommentVotes.DoesNotExist:
            ElectNewCommentVotes.objects.create(comment=self, user=user, vote=ElectNewCommentVotes.LIKE)
            self.like += 1
            self.save(update_fields=['like'])
            if self.parent:
                if community:
                    from common.notify.notify import community_notify, community_wall
                    community_notify(user, community, None, self.pk, "ELNC", "u_elect_new_comment_notify", "LRE")
                    community_wall(user, community, None, self.pk, "ELNC", "u_elect_new_comment_notify", "LCO")
                else:
                    from common.notify.notify import user_notify, user_wall
                    user_notify(user, None, self.pk, "ELNC", "u_elect_new_comment_notify", "LRE")
                    user_wall(user, None, self.pk, "ELNC", "u_elect_new_comment_notify", "LCO")
            else:
                if community:
                    from common.notify.notify import community_notify, community_wall
                    community_notify(user, community, None, self.pk, "PHOC", "u_elect_new_comment_notify", "LCO")
                    community_wall(user, community, None, self.pk, "PHOC", "u_elect_new_comment_notify", "LCO")
                else:
                    from common.notify.notify import user_notify, user_wall
                    user_notify(user, None, self.pk, "ELNC", "u_elect_new_comment_notify", "LCO")
                    user_wall(user, None, self.pk, "ELNC", "u_elect_new_comment_notify", "LCO")
        return HttpResponse(json.dumps({"like_count": str(self.like)}),content_type="application/json")
