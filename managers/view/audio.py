from django.views import View
from users.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from common.staff_progs.audio import *
from music.models import Music, SoundList
from django.views.generic.base import TemplateView
from managers.models import Moderated
from django.http import Http404
from common.templates import get_detect_platform_template
from logs.model.manage_audio import AudioManageLog
from managers.forms import ModeratedForm, ReportForm


class AudioAdminCreate(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and (request.user.is_superuser or request.user.is_work_audio_administrator()):
            add_audio_administrator(user, request.user)
            return HttpResponse()
        else:
            raise Http404

class AudioAdminDelete(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and (request.user.is_superuser or request.user.is_work_audio_administrator()):
            remove_audio_administrator(user, request.user)
            return HttpResponse()
        else:
            raise Http404


class AudioModerCreate(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and (request.user.is_superuser or request.user.is_work_audio_moderator()):
            add_audio_moderator(user, request.user)
            return HttpResponse()
        else:
            raise Http404

class AudioModerDelete(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and (request.user.is_superuser or request.user.is_work_audio_moderator()):
            remove_audio_moderator(user, request.user)
            return HttpResponse()
        else:
            raise Http404


class AudioEditorCreate(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and (request.user.is_superuser or request.user.is_work_audio_editor()):
            add_audio_editor(user, request.user)
            return HttpResponse()
        else:
            raise Http404

class AudioEditorDelete(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and (request.user.is_superuser or request.user.is_work_audio_editor()):
            remove_audio_editor(user, request.user)
            return HttpResponse()
        else:
            raise Http404


class AudioWorkerAdminCreate(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.is_superuser:
            add_audio_administrator_worker(user, request.user)
            return HttpResponse()
        else:
            raise Http404

class AudioWorkerAdminDelete(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.is_superuser:
            remove_audio_administrator_worker(user, request.user)
            return HttpResponse()
        else:
            raise Http404


class AudioWorkerModerCreate(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.is_superuser:
            add_audio_moderator_worker(user, request.user)
            return HttpResponse()
        else:
            raise Http404

class AudioWorkerModerDelete(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.is_superuser:
            remove_audio_moderator_worker(user, request.user)
            return HttpResponse()
        else:
            raise Http404


class AudioWorkerEditorCreate(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.is_superuser:
            add_audio_editor_worker(user, request.user)
            return HttpResponse()
        else:
            raise Http404

class AudioWorkerEditorDelete(View):
    def get(self,request,*args,**kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.is_superuser:
            remove_audio_editor_worker(user, request.user)
            return HttpResponse()
        else:
            raise Http404


class AudioCloseCreate(View):
    template_name = None

    def get(self,request,*args,**kwargs):
        if request.is_ajax() and request.user.is_audio_manager():
            self.template_name = get_detect_platform_template("managers/manage_create/audio/audio_close.html", request.user, request.META['HTTP_USER_AGENT'])
        else:
            raise Http404
        return super(AudioCloseCreate,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(AudioCloseCreate,self).get_context_data(**kwargs)
        context["object"] = Music.objects.get(pk=self.kwargs["pk"])
        return context

    def post(self,request,*args,**kwargs):
        from managers.forms import ModeratedForm

        audio, form = Music.objects.get(pk=self.kwargs["pk"]), ModeratedForm(request.POST)
        if request.is_ajax() and form.is_valid() and request.user.is_audio_manager():
            mod = form.save(commit=False)
            moderate_obj = Moderated.get_or_create_moderated_object(object_id=audio.pk, type="MUS")
            moderate_obj.create_close(object=audio, description=mod.description, manager_id=request.user.pk)
            AudioManageLog.objects.create(item=audio.pk, manager=manager_id, action_type=AudioManageLog.ITEM_CLOSED)
            return HttpResponse()
        else:
            return HttpResponseBadRequest()

class AudioCloseDelete(View):
    def get(self,request,*args,**kwargs):
        audio = Music.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.is_audio_manager():
            moderate_obj = Moderated.objects.get(object_id=audio.pk, type="MUS")
            moderate_obj.delete_close(object=audio, manager_id=request.user.pk)
            AudioManageLog.objects.create(item=audio.pk, manager=manager_id, action_type=AudioManageLog.ITEM_CLOSED_HIDE)
            return HttpResponse()
        else:
            raise Http404


class AudioClaimCreate(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        from managers.models import ModerationReport

        self.track = Music.objects.get(pk=self.kwargs["pk"])
        self.is_reported = ModerationReport.is_user_already_reported(request.user.pk, 'MUL', self.track.pk)
        self.template_name = get_detect_platform_template("managers/manage_create/audio/audio_claim.html", request.user, request.META['HTTP_USER_AGENT'])
        return super(AudioClaimCreate,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        from managers.forms import ReportForm

        context = super(AudioClaimCreate,self).get_context_data(**kwargs)
        context["object"] = self.track
        context["is_reported"] = self.is_reported
        context["form"] = ReportForm()
        return context

    def post(self,request,*args,**kwargs):
        from managers.models import ModerationReport
        from managers.forms import ReportForm

        form = ReportForm(request.POST)
        music = Music.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and form.is_valid() and not ModerationReport.is_user_already_reported(request.user.pk, 'MUS', music.pk):
            claim = form.save(commit=False)
            type = request.POST.get('type')
            ModerationReport.create_moderation_report(reporter_id=request.user.pk, _type="MUS", object_id=music.pk, description=claim.description, type=type)
            return HttpResponse()
        else:
            return HttpResponseBadRequest()

class AudioRejectedCreate(View):
    def get(self,request,*args,**kwargs):
        if request.is_ajax() and request.user.is_audio_manager():
            music = Music.objects.get(pk=self.kwargs["pk"])
            moderate_obj = Moderated.objects.get(object_id=music.pk, type="MUS")
            moderate_obj.reject_moderation(manager_id=request.user.pk)
            AudioManageLog.objects.create(item=music.pk, manager=manager_id, action_type=AudioManageLog.ITEM_REJECT)
            return HttpResponse()
        else:
            raise Http404


class AudioUnverify(View):
    def get(self,request,*args,**kwargs):
        music = Music.objects.get(pk=self.kwargs["pk"])
        obj = Moderated.get_or_create_moderated_object(object_id=music.pk, type="MUS")
        if request.is_ajax() and request.user.is_audio_manager():
            obj.unverify_moderation(music, manager_id=request.user.pk)
            AudioManageLog.objects.create(item=obj.object_id, manager=manager_id, action_type=AudioManageLog.ITEM_UNVERIFY)
            return HttpResponse()
        else:
            raise Http404


class ListAudioClaimCreate(View):
    template_name = None

    def get(self,request,*args,**kwargs):
        from managers.models import ModerationReport

        self.list = SoundList.objects.get(uuid=self.kwargs["uuid"])
        self.is_reported = ModerationReport.is_user_already_reported(request.user.pk, 'ELEC', self.list.pk)
        self.template_name = get_detect_platform_template("managers/manage_create/audio/list_claim.html", request.user, request.META['HTTP_USER_AGENT'])
        return super(ListAudioClaimCreate,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(ListAudioClaimCreate,self).get_context_data(**kwargs)
        context["list"] = self.list
        context["is_reported"] = self.is_reported
        return context

    def post(self,request,*args,**kwargs):
        from managers.models import ModerationReport

        self.list = SoundList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax():
            description = request.POST.get('description')
            type = request.POST.get('type')
            ModerationReport.create_moderation_report(reporter_id=request.user.pk, _type="MUL", object_id=list.pk, description=description, type=type)
            return HttpResponse()
        else:
            return HttpResponseBadRequest()

class ListAudioRejectedCreate(View):
    def get(self,request,*args,**kwargs):
        list = SoundList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and request.user.is_audio_manager():
            moderate_obj = Moderated.objects.get(object_id=list.pk, type="MUL")
            moderate_obj.reject_moderation(manager_id=request.user.pk)
            AudioManageLog.objects.create(item=list.pk, manager=request.user.pk, action_type=AudioManageLog.LIST_REJECT)
            return HttpResponse()
        else:
            raise Http404


class ListAudioUnverify(View):
    def get(self,request,*args,**kwargs):
        list = SoundList.objects.get(uuid=self.kwargs["uuid"])
        obj = Moderated.get_or_create_moderated_object(object_id=list.pk, type="MUL")
        if request.is_ajax() and request.user.is_audio_manager():
            obj.unverify_moderation(list, manager_id=request.user.pk)
            AudioManageLog.objects.create(item=list.pk, manager=request.user.pk, action_type=AudioManageLog.LIST_UNVERIFY)
            return HttpResponse()
        else:
            raise Http404

class ListAudioCloseCreate(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.list = SoundList.objects.get(uuid=self.kwargs["uuid"])
        if request.user.is_audio_manager():
            self.template_name = get_detect_platform_template("managers/manage_create/audio/list_close.html", request.user, request.META['HTTP_USER_AGENT'])
        else:
            raise Http404
        return super(ListAudioCloseCreate,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(ListAudioCloseCreate,self).get_context_data(**kwargs)
        context["list"] = self.list
        return context

    def post(self,request,*args,**kwargs):
        list = SoundList.objects.get(uuid=self.kwargs["uuid"])
        form = ModeratedForm(request.POST)
        if form.is_valid() and request.user.is_audio_manager():
            mod = form.save(commit=False)
            moderate_obj = Moderated.get_or_create_moderated_object(object_id=list.pk, type="MUL")
            moderate_obj.create_close(object=list, description=mod.description, manager_id=request.user.pk)
            AudioManageLog.objects.create(item=list.pk, manager=request.user.pk, action_type=AudioManageLog.LIST_CLOSED)
            return HttpResponse()
        else:
            return HttpResponseBadRequest()

class ListAudioCloseDelete(View):
    def get(self,request,*args,**kwargs):
        list = SoundList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and request.user.is_audio_manager():
            moderate_obj = Moderated.objects.get(object_id=list.pk, type="MUL")
            moderate_obj.delete_close(object=list, manager_id=request.user.pk)
            AudioManageLog.objects.create(item=list.pk, manager=request.user.pk, action_type=AudioManageLog.LIST_CLOSED_HIDE)
            return HttpResponse()
        else:
            raise Http404
