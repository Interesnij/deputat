from docs.models import Doc, DocList
from users.models import User
from django.views import View
from django.views.generic.base import TemplateView
from rest_framework.exceptions import PermissionDenied
from docs.forms import DoclistForm, DocForm
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import Http404
from common.templates import render_for_platform


class UserDoclistAdd(View):
    def get(self,request,*args,**kwargs):
        list = DocList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and list.is_user_can_add_list(request.user.pk):
            list.users.add(request.user)
        return HttpResponse()

class UserDoclistRemove(View):
    def get(self,request,*args,**kwargs):
        list = DocList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and list.is_user_can_delete_list(request.user.pk):
            list.users.remove(request.user)
        return HttpResponse()


class UserDocAdd(View):
    def get(self, request, *args, **kwargs):
        doc, list = Doc.objects.get(pk=self.kwargs["pk"]), DocList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and not list.is_doc_in_list(doc.pk):
            list.doc_list.add(doc)
            return HttpResponse()
        else:
            raise Http404

class UserDocRemove(View):
    def get(self, request, *args, **kwargs):
        doc = Doc.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and list.is_doc_in_list(doc.pk):
            doc.remove()
            return HttpResponse()
        else:
            raise Http404

class UserDocListAdd(View):
    def get(self, request, *args, **kwargs):
        doc, list = Doc.objects.get(pk=self.kwargs["pk"]), DocList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and not list.is_doc_in_list(doc.pk):
            list.doc_list.add(doc)
            return HttpResponse()
        else:
            raise Http404

class UserDocListRemove(View):
    def get(self, request, *args, **kwargs):
        doc, list = Doc.objects.get(pk=self.kwargs["pk"]), DocList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and list.is_doc_in_list(doc.pk):
            list.doc_list.remove(doc)
            return HttpResponse()
        else:
            raise Http404

class UserCreateDoclistWindow(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.user, self.template_name = User.objects.get(pk=self.kwargs["pk"]), get_small_template("user_docs/create_doc_list.html", request.user, request.META['HTTP_USER_AGENT'])
        return super(UserCreateDoclistWindow,self).get(request,*args,**kwargs)

class UserCreateDocWindow(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.user, self.template_name = User.objects.get(pk=self.kwargs["pk"]), get_small_template("user_docs/", request.user, request.META['HTTP_USER_AGENT'])
        return super(UserCreateDocWindow,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(UserCreateDocWindow,self).get_context_data(**kwargs)
        context["form_post"] = DocForm()
        return context


class UserDoclistCreate(View):
    form_post = None

    def get_context_data(self,**kwargs):
        context = super(UserDoclistCreate,self).get_context_data(**kwargs)
        context["form_post"] = DoclistForm()
        return context

    def post(self,request,*args,**kwargs):
        form_post= DoclistForm(request.POST)
        if request.is_ajax() and form_post.is_valid():
            new_list = form_post.save(commit=False)
            new_list.creator = request.user
            if not new_list.order:
                new_list.order = 0
            new_list.save()
            return render_for_platform(request, 'user_docs/list.html',{'list': new_list, 'user': request.user})
        else:
            return HttpResponseBadRequest()


class UserDocCreate(View):
    form_post = None

    def get_context_data(self,**kwargs):
        context = super(UserDocCreate,self).get_context_data(**kwargs)
        context["form_post"] = DocForm()
        return context

    def post(self,request,*args,**kwargs):
        form_post, user = DocForm(request.POST, request.FILES), User.objects.get(pk=self.kwargs["pk"])

        if request.is_ajax() and form_post.is_valid() and request.user == user:
            list, new_doc = DocList.objects.get(creator_id=user.pk, type=DocList.MAIN), form_post.save(commit=False)
            new_doc.creator_id = request.user.pk
            lists = form_post.cleaned_data.get("list")
            new_doc.save()
            for _list in lists:
                _list.doc_list.add(new_doc)
            user_notify(request.user, new_post.creator.pk, None, "doc"+str(new_doc.pk), "u_doc_create", "ITE")
            return render_for_platform(request, 'user_docs/new_doc.html',{'object': new_doc})
        else:
            return HttpResponseBadRequest()


class UserDoclistEdit(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.user, self.template_name = User.objects.get(pk=self.kwargs["pk"]), get_small_template("user_docs/edit_list.html", request.user, request.META['HTTP_USER_AGENT'])
        return super(UserDoclistEdit,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(UserDoclistEdit,self).get_context_data(**kwargs)
        context["user"] = self.user
        context["list"] = DocList.objects.get(uuid=self.kwargs["uuid"])
        return context

    def post(self,request,*args,**kwargs):
        self.list = DocList.objects.get(uuid=self.kwargs["uuid"])
        self.form, self.user = DoclistForm(request.POST,instance=self.list), User.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and self.form.is_valid() and self.user == request.user:
            list = self.form.save(commit=False)
            self.form.save()
            return HttpResponse()
        else:
            return HttpResponseBadRequest()
        return super(UserDoclistEdit,self).get(request,*args,**kwargs)

class UserDoclistDelete(View):
    def get(self,request,*args,**kwargs):
        list = DocList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and self.kwargs["pk"] == request.user.pk and list.type == DocList.LIST:
            list.type = "DEL"
            list.save(update_fields=['type'])
            return HttpResponse()
        else:
            raise Http404

class UserDoclistAbortDelete(View):
    def get(self,request,*args,**kwargs):
        list = DocList.objects.get(uuid=self.kwargs["uuid"])
        if request.is_ajax() and self.kwargs["pk"] == request.user.pk:
            list.type = "PUB"
            list.save(update_fields=['type'])
            return HttpResponse()
        else:
            raise Http404
