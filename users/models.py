from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from common.utils import try_except
from users.helpers import upload_to_user_directory
from city.models import City

"""
    Группируем все таблицы пользователя здесь:
    1. Сам пользователь
"""

class User(AbstractUser):
    DELETED, BLOCKED, PHONE_NO_VERIFIED, STANDART, MANAGER, SUPERMANAGER = 'DE', 'BL', 'PV', 'ST', 'MA', 'SM'
    MALE, FEMALE, DESCTOP, PHONE = 'Man', 'Fem', 'De', 'Ph'
    PERM = (
        (DELETED, 'Удален'),
        (BLOCKED, 'Заблокирован'),
        (PHONE_NO_VERIFIED, 'Телефон не подтвержден'),
        (STANDART, 'Обычные права'),
        (MANAGER, 'Менеджер'),
        (SUPERMANAGER, 'Суперменеджер'),
    )
    GENDER, DEVICE = ((MALE, 'Мужской'),(FEMALE, 'Женский'),), ((DESCTOP, 'Комп'),(PHONE, 'Телефон'),)

    last_activity = models.DateTimeField(default=timezone.now, blank=True, verbose_name='Активность')
    phone = models.CharField(max_length=17, blank=True, null=True, verbose_name='Телефон')
    perm = models.CharField(max_length=5, choices=PERM, default=PHONE_NO_VERIFIED, verbose_name="Уровень доступа")
    #b_avatar = models.ImageField(blank=True, upload_to=upload_to_user_directory)
    s_avatar = models.ImageField(blank=True, upload_to=upload_to_user_directory)
    gender = models.CharField(max_length=5, choices=GENDER, blank=True, verbose_name="Пол")
    device = models.CharField(max_length=5, choices=DEVICE, blank=True, verbose_name="Оборудование")
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL, verbose_name="Город")
    point = models.PositiveIntegerField(default=0, verbose_name="Количество кармы")
    level = models.PositiveSmallIntegerField(default=1, verbose_name="Уровень")
    USERNAME_FIELD = 'phone'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return str(self.phone)

    def get_verb_gender(self, verb):
        if self.is_women():
            return "W" + verb
        else:
            return verb

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_region_slug(self):
        return self.city.region.slug

    def get_joined(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.last_activity)

    def get_location(self):
        from users.model.profile import UserLocation

        if UserLocation.objects.filter(user=self).exists():
            return UserLocation.objects.filter(user=self).first()
        else:
            return False

    def is_online(self):
        from datetime import datetime, timedelta

        now = datetime.now()
        onl = self.last_activity + timedelta(minutes=5)
        if now < onl:
            return True
        else:
            return False

    def get_news(self):
        from blog.models import ElectNew
        return ElectNew.objects.filter(creator_id=self.pk)

    def get_news_count(self):
        from blog.models import ElectNew
        return ElectNew.objects.filter(creator_id=self.pk).values("pk").count()

    def get_elect_subscribers(self):
        from elect.models import Elect, SubscribeElect

        elect_subscribers = SubscribeElect.objects.filter(user_id=self.pk).values("elect_id")
        elect_ids = [elect['elect_id'] for elect in elect_subscribers]
        return Elect.objects.filter(id__in=elect_ids)

    def is_have_elect_subscribers(self):
        from elect.models import Elect, SubscribeElect

        elect_subscribers = SubscribeElect.objects.filter(user_id=self.pk).values("elect_id")
        elect_ids = [elect['elect_id'] for elect in elect_subscribers]
        return Elect.objects.filter(id__in=elect_ids).exists()

    def get_elect_subscribers_count(self):
        from elect.models import SubscribeElect
        return SubscribeElect.objects.filter(user_id=self.pk).values("pk").count()

    def get_like_news(self):
        from common.model.votes import ElectNewVotes2
        from blog.models import ElectNew

        likes = ElectNewVotes2.objects.filter(user_id=self.pk, vote=ElectNewVotes2.LIKE).values("new_id")
        news_ids = [new['new_id'] for new in likes]
        return ElectNew.objects.filter(id__in=news_ids)

    def get_like_news_count(self):
        from common.model.votes import ElectNewVotes2
        return ElectNewVotes2.objects.filter(user_id=self.pk, vote=ElectNewVotes2.LIKE).values("new_id").count()

    def get_dislike_news(self):
        from common.model.votes import ElectNewVotes2
        from blog.models import ElectNew

        dislikes = ElectNewVotes2.objects.filter(user_id=self.pk, vote=ElectNewVotes2.DISLIKE).values("new_id")
        news_ids = [new['new_id'] for new in dislikes]
        return ElectNew.objects.filter(id__in=news_ids)

    def get_dislike_news_count(self):
        from common.model.votes import ElectNewVotes2
        return ElectNewVotes2.objects.filter(user_id=self.pk, vote=ElectNewVotes2.DISLIKE).values("new_id").count()

    def is_deleted(self):
        return try_except(self.perm == User.DELETED)
    def is_blocked(self):
        return try_except(self.perm == User.BLOCKED)
    def is_manager(self):
        return try_except(self.perm == User.MANAGER)
    def is_supermanager(self):
        return try_except(self.perm == User.SUPERMANAGER)
    def is_no_phone_verified(self):
        return try_except(self.perm == User.PHONE_NO_VERIFIED)

    def is_man(self):
        if self.gender == User.MALE:
            return True
        else:
            return False
    def is_women(self):
        if self.gender == User.FEMALE:
            return True
        else:
            return False

    def create_s_avatar(self, photo_input):
        from easy_thumbnails.files import get_thumbnailer

        self.s_avatar = photo_input
        self.save(update_fields=['s_avatar'])
        new_img = get_thumbnailer(self.s_avatar)['small_avatar'].url.replace('media/', '')
        self.s_avatar = new_img
        return self.save(update_fields=['s_avatar'])

    def get_avatar(self):
        try:
            return self.s_avatar.url
        except:
            return '/static/images/user.png'

    def get_last_activity(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime

        return naturaltime(self.last_activity)

    def get_country(self):
        from users.model.profile import UserLocation

        return UserLocation.objects.filter(user_id=self.pk).last().country_ru

    def get_online_display(self):
        from datetime import datetime, timedelta

        now = datetime.now()
        onl = self.last_activity + timedelta(minutes=3)
        if self.device == User.DESCTOP:
            device = '&nbsp;<svg style="width: 17px;" class="svg_default" fill="currentColor" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="none"/><path d="M20 18c1.1 0 1.99-.9 1.99-2L22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H0v2h24v-2h-4zM4 6h16v10H4V6z"/></svg>'
        else:
            device = '&nbsp;<svg style="width: 17px;" class="svg_default" fill="currentColor" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="none"/><path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>'
        if now < onl:
            return '<i>Онлайн</i>' + device
        else:
            if self.is_women():
                return '<i>Была ' + self.get_last_activity() + '</i>' + device
            else:
                return '<i>Был ' + self.get_last_activity() + '</i>' + device

    def get_user_news_notify_ids(self):
        from notify.models import UserNewsNotify
        return [i['target'] for i in UserNewsNotify.objects.filter(user=self.pk).values('target')]

    def get_user_profile_notify_ids(self):
        from notify.models import UserProfileNotify
        return [i['target'] for i in UserProfileNotify.objects.filter(user=self.pk).values('target')]

    def get_user_notify(self):
        from notify.models import Notify

        query = Q(creator_id__in=self.get_user_profile_notify_ids())
        query.add(Q(user_set__isnull=True, object_set__isnull=True), Q.AND)
        return Notify.objects.only('created').filter(query)

    def read_user_notify(self):
        from notify.models import Notify
        Notify.u_notify_unread(self.pk)

    def count_unread_notify(self):
        from notify.models import Notify
        query = Q(recipient_id=self.pk, status="U")
        return Notify.objects.filter(query).values("pk").count()

    def unread_notify_count(self):
        count = self.count_unread_notify()
        if count > 0:
            return '<span class="tab_badge badge-success" style="font-size: 60%;">' + str(count) + '</span>'
        else:
            return ''

    def get_member_for_notify_ids(self):
        from notify.models import UserProfileNotify
        return [i['target'] for i in UserProfileNotify.objects.filter(user=self.pk).values("target")]

    def add_news_subscriber(self, user_id):
        from notify.models import UserNewsNotify
        if not UserNewsNotify.objects.filter(user=self.pk, target=user_id).exists():
            UserNewsNotify.objects.create(user=self.pk, target=user_id)
    def delete_news_subscriber(self, user_id):
        from notify.models import UserNewsNotify
        if UserNewsNotify.objects.filter(user=self.pk, target=user_id).exists():
            notify = UserNewsNotify.objects.get(user=self.pk, target=user_id)
            notify.delete()

    def add_notify_subscriber(self, user_id):
        from notify.models import UserProfileNotify
        if not UserProfileNotify.objects.filter(user=self.pk, target=user_id).exists():
            UserProfileNotify.objects.create(user=self.pk, target=user_id)
    def delete_notify_subscriber(self, user_id):
        from notify.models import UserProfileNotify
        if UserProfileNotify.objects.filter(user=self.pk, target=user_id).exists():
            notify = UserProfileNotify.objects.get(user=self.pk, target=user_id)
            notify.delete()
