from django.views.generic.base import TemplateView
from users.models import User
from gallery.models import Album, Photo
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.http import Http404
from common.utils import get_small_template


class UserLoadAlbum(ListView):
	template_name, paginate_by = None, 15

	def get(self,request,*args,**kwargs):
		self.album = Album.objects.get(uuid=self.kwargs["uuid"])
		self.template_name = get_small_template("user_gallery/load_list.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(UserLoadAlbum,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		c = super(UserLoadAlbum,self).get_context_data(**kwargs)
		c['user'], c['album'] = self.album.creator, self.album
		return c

	def get_queryset(self):
		list = self.album.get_photos()
		return list


class UserPhotosList(ListView):
    template_name, paginate_by = None, 15

    def get(self,request,*args,**kwargs):
        self.user = User.objects.get(pk=self.kwargs["pk"])
        self.album = Album.objects.get(uuid=self.kwargs["uuid"])
        self.template_name = get_small_template(self.album, "user_gallery/list.html", request.user, request.META['HTTP_USER_AGENT'])
        return super(UserPhotosList,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(UserPhotosList,self).get_context_data(**kwargs)
        context['user'] = self.user
        context['album'] = self.album
        return context

    def get_queryset(self):
        photo_list = self.album.get_photos()
        return photo_list


class UserAlbumPhoto(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.photo = Photo.objects.get(pk=self.kwargs["pk"])
        self.album = Album.objects.get(uuid=self.kwargs["uuid"])
        self.photos = self.album.get_photos()
        if request.is_ajax():
            self.template_name = get_small_template("user_gallery/photo.html", request.user, request.META['HTTP_USER_AGENT'])
        else:
            raise Http404
        return super(UserAlbumPhoto,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(UserAlbumPhoto,self).get_context_data(**kwargs)
        context["object"] = self.photo
        context["album"] = self.album
        context["next"] = self.photos.filter(pk__gt=self.photo.pk, is_deleted=False).order_by('pk').first()
        context["prev"] = self.photos.filter(pk__lt=self.photo.pk, is_deleted=False).order_by('-pk').first()
        return context


class UserElectNewPhoto(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from blog.models import ElectNew

		self.photo = Photo.objects.get(pk=self.kwargs["photo_pk"])
		self.elect_new = ElectNew.objects.get(pk=self.kwargs["pk"])
		self.photos = self.elect_new.get_attach_photos()
		if request.is_ajax():
			self.template_name = get_small_template("user_gallery/elect_new_photo.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			raise Http404
		return super(UserElectNewPhoto,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserElectNewPhoto,self).get_context_data(**kwargs)
		context["object"] = self.photo
		context["elect_new"] = self.elect_new
		context["user"] = self.request.user
		context["next"] = self.photos.filter(pk__gt=self.photo.pk, is_deleted=False).order_by('pk').first()
		context["prev"] = self.photos.filter(pk__lt=self.photo.pk, is_deleted=False).order_by('-pk').first()
		return context

class UserCommentPhoto(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.model.comments import ElectNewComment

		self.photo = Photo.objects.get(pk=self.kwargs["photo_pk"])
		self.comment = PostComment.objects.get(pk=self.kwargs["pk"])
		self.photos = self.comment.get_attach_photos()
		if request.is_ajax():
			self.template_name = get_small_template("user_gallery/elect_new_comment_photo.html.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			raise Http404
		return super(UserCommentPhoto,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserCommentPhoto,self).get_context_data(**kwargs)
		context["object"] = self.photo
		context["user"] = self.request.user
		context["next"] = self.photos.filter(pk__gt=self.photo.pk, is_deleted=False).order_by('pk').first()
		context["prev"] = self.photos.filter(pk__lt=self.photo.pk, is_deleted=False).order_by('-pk').first()
		return context


class GetUserPhoto(TemplateView):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.photo = Photo.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax():
            self.template_name = get_small_template("user_gallery/get_photo.html", request.user, request.META['HTTP_USER_AGENT'])
        else:
            raise Http404
        return super(GetUserPhoto,self).get(request,*args,**kwargs)

    def get_context_data(self,**kwargs):
        context = super(GetUserPhoto,self).get_context_data(**kwargs)
        context["object"] = self.photo
        return context
