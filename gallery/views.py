from django.views.generic.base import TemplateView
from django.views.generic import ListView
from gallery.models import Album, Photo


class UserLoadAlbum(ListView):
	template_name, paginate_by = None, 15

	def get(self,request,*args,**kwargs):
		from common.templates import get_list_template

		self.album = Album.objects.get(pk=self.kwargs["pk"])
		self.template_name = get_list_template(self.album, "user_gallery/load_list/", "a.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(UserLoadAlbum,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		c = super(UserLoadAlbum,self).get_context_data(**kwargs)
		c['user'], c['album'] = self.album.creator, self.album
		return c

	def get_queryset(self):
		list = self.album.get_photos()
		return list


class UserGallery(ListView):
	template_name, paginate_by = None, 15

	def get(self,request,*args,**kwargs):
		from common.templates import get_list_template
		from users.models import User

		self.user = User.objects.get(pk=self.kwargs["pk"])
		self.album = self.user.get_or_create_main_album()
		if self.user.pk == request.user.pk:
			self.photo_list = self.album.get_staff_photos()
		else:
			self.photo_list = self.album.get_photos()
		self.template_name = get_list_template(self.album, "user_gallery/gallery/", "a.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(UserGallery,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserGallery,self).get_context_data(**kwargs)
		context['user'] = self.user
		context['album'] = self.album
		return context
	def get_queryset(self):
		return self.photo_list


class UserAlbum(ListView):
	template_name, paginate_by = None, 12

	def get(self,request,*args,**kwargs):
		from common.templates import get_list_template
		from users.models import User

		self.user = User.objects.get(pk=self.kwargs["pk"])
		self.album = Album.objects.get(uuid=self.kwargs["uuid"])
		if self.user.pk == request.user.pk:
			self.photo_list = self.album.get_staff_photos()
		else:
			self.photo_list = self.album.get_photos()
		self.template_name = get_list_template(self.album, "user_gallery/album/", "a.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(UserAlbum,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserAlbum,self).get_context_data(**kwargs)
		context['user'] = self.user
		context['album'] = self.album
		return context

	def get_queryset(self):
		return self.photo_list


class UserAlbumPhoto(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.templates import get_item_template
		from django.db.models import Q

		self.photo, self.album = Photo.objects.get(pk=self.kwargs["pk"]), Album.objects.get(uuid=self.kwargs["uuid"])
		if request.is_ajax():
			self.template_name = get_item_template(self.photo, "user_gallery/photo/", "a.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			from django.http import Http404
			raise Http404
		if request.user.pk == self.photo.creator.pk:
			query = Q(type="PUB") | Q(type="PRI")
			self.photos = self.album.get_photos()
		else:
			query = Q(type="PUB")
			self.photos = self.album.get_staff_photos()
		self.next = self.photos.filter(query, pk__gt=self.photo.pk, ).order_by('pk').first()
		self.prev = self.photos.filter(query, pk__lt=self.photo.pk).order_by('pk').first()
		return super(UserAlbumPhoto,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserAlbumPhoto,self).get_context_data(**kwargs)
		context["object"] = self.photo
		context["album"] = self.album
		context["next"] = self.next
		context["prev"] = self.prev
		return context


class UserElectNewPhoto(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from blog.models import ElectNew
		from common.templates import get_item_template

		self.photo = Photo.objects.get(pk=self.kwargs["photo_pk"])
		self.elect_new = ElectNew.objects.get(pk=self.kwargs["pk"])
		self.photos = self.elect_new.get_attach_photos()
		if request.is_ajax():
			self.template_name = get_item_template(self.photo, "user_gallery/photo/", "a.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			from django.http import Http404
			raise Http404
		return super(UserElectNewPhoto,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserElectNewPhoto,self).get_context_data(**kwargs)
		context["object"] = self.photo
		context["elect_new"] = self.elect_new
		context["user"] = self.request.user
		context["next"] = self.photos.filter(pk__gt=self.photo.pk, type="PUB").order_by('pk').first()
		context["prev"] = self.photos.filter(pk__lt=self.photo.pk, type="PUB").order_by('-pk').first()
		return context

class UserBlogCommentPhoto(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.model.comments import BlogComment
		from common.templates import get_item_template

		self.photo = Photo.objects.get(pk=self.kwargs["photo_pk"])
		self.comment = BlogComment.objects.get(pk=self.kwargs["pk"])
		self.photos = self.comment.get_attach_photos()
		if request.is_ajax():
			self.template_name = get_item_template(self.photo, "user_gallery/blog_comment_photo/", "a.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			from django.http import Http404
			raise Http404
		return super(UserBlogCommentPhoto,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserBlogCommentPhoto,self).get_context_data(**kwargs)
		context["object"] = self.photo
		context["user"] = self.request.user
		context["next"] = self.photos.filter(pk__gt=self.photo.pk, type="PUB").order_by('pk').first()
		context["prev"] = self.photos.filter(pk__lt=self.photo.pk, type="PUB").order_by('-pk').first()
		context["comment"] = self.comment
		return context

class UserElectNewCommentPhoto(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.model.comments import ElectNewComment
		from common.templates import get_item_template

		self.photo = Photo.objects.get(pk=self.kwargs["photo_pk"])
		self.comment = ElectNewComment.objects.get(pk=self.kwargs["pk"])
		self.photos = self.comment.get_attach_photos()
		if request.is_ajax():
			self.template_name = get_item_template(self.photo, "user_gallery/elect_new_comment_photo/", "a.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			from django.http import Http404
			raise Http404
		return super(UserElectNewCommentPhoto,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(UserElectNewCommentPhoto,self).get_context_data(**kwargs)
		context["object"] = self.photo
		context["user"] = self.request.user
		context["next"] = self.photos.filter(pk__gt=self.photo.pk, type="PUB").order_by('pk').first()
		context["prev"] = self.photos.filter(pk__lt=self.photo.pk, type="PUB").order_by('-pk').first()
		context["comment"] = self.comment
		return context


class GetUserPhoto(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		from common.templates import get_small_template
		self.photo = Photo.objects.get(pk=self.kwargs["pk"])
		if request.is_ajax():
			self.template_name = get_small_template("user_gallery/get_photo.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			from django.http import Http404
			raise Http404
		return super(GetUserPhoto,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context = super(GetUserPhoto,self).get_context_data(**kwargs)
		context["object"] = self.photo
		return context
