from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin
from users.models import User
from django.views.generic import ListView
from common.templates import get_small_template, get_my_template
from django.http import HttpResponse


class AuthView(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		if request.user.is_authenticated:
			self.template_name = "profile/user_news.html"
		else:
			self.template_name = "account/login.html"
		return super(AuthView,self).get(request,*args,**kwargs)

class SignupView(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		if request.user.is_authenticated:
			self.template_name = "profile/user_news.html"
		else:
			self.template_name = "account/signup.html"
		return super(SignupView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		from region.models import Region
		context=super(SignupView,self).get_context_data(**kwargs)
		context["regions"] = Region.objects.only("pk")
		return context

class MainPhoneSend(TemplateView):
	template_name = None

	def get(self,request,*args,**kwargs):
		if request.user.is_no_phone_verified():
			self.template_name = get_small_template("generic/phone_verification.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			self.template_name = get_small_template("profile/user.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(MainPhoneSend,self).get(request,*args,**kwargs)

class UserNewsView(ListView, CategoryListMixin):
	template_name = None
	paginate_by = 15

	def get(self,request,*args,**kwargs):
		from common.templates import get_template_user, get_template_anon_user

		self.user = User.objects.get(pk=self.kwargs["pk"])
		if self.user.pk == request.user.pk:
			self.user_news = self.user.get_my_news()
		else:
			self.user_news = self.user.get_news()
		if request.user.is_authenticated:
			self.template_name = get_template_user(self.user, "profile/news/", "news.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			self.template_name = get_template_anon_user(self.user, "profile/news/", "news.html", request.META['HTTP_USER_AGENT'])
		return super(UserNewsView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super(UserNewsView,self).get_context_data(**kwargs)
		context["user"] = self.user
		return context

	def get_queryset(self):
		return self.user_news


class SubscribeElectsView(ListView, CategoryListMixin):
	template_name = None
	paginate_by = 15

	def get(self,request,*args,**kwargs):
		self.user = User.objects.get(pk=self.kwargs["pk"])
		self.template_name = get_small_template("profile/subscribes_elect.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(SubscribeElectsView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super(SubscribeElectsView,self).get_context_data(**kwargs)
		context["user"] = self.user
		return context

	def get_queryset(self):
		elect_subscribers = self.user.get_elect_subscribers()
		return elect_subscribers


class LikeNewsView(ListView, CategoryListMixin):
	template_name = None
	paginate_by = 15

	def get(self,request,*args,**kwargs):
		self.user = User.objects.get(pk=self.kwargs["pk"])
		self.template_name = get_small_template("profile/like_news.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(LikeNewsView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super(LikeNewsView,self).get_context_data(**kwargs)
		context["user"] = self.user
		return context

	def get_queryset(self):
		like_news = self.user.get_like_news()
		return like_news


class DislikeNewsView(ListView, CategoryListMixin):
	template_name = None
	paginate_by = 15

	def get(self,request,*args,**kwargs):
		self.user = User.objects.get(pk=self.kwargs["pk"])
		self.template_name = get_small_template("profile/dislike_news.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(DislikeNewsView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super(DislikeNewsView,self).get_context_data(**kwargs)
		context["user"] = self.user
		return context

	def get_queryset(self):
		dislike_news = self.user.get_dislike_news()
		return dislike_news


class UserView(TemplateView, CategoryListMixin):
	template_name = "profile/user.html"

	def get(self,request,*args,**kwargs):
		from common.templates import get_template_user, get_template_anon_user
		self.user = User.objects.get(pk=self.kwargs["pk"])
		if request.user.is_authenticated:
			self.template_name = get_template_user(self.user, "profile/user/", "user.html", request.user, request.META['HTTP_USER_AGENT'])
		else:
			self.template_name = get_template_anon_user(self.user, "profile/user/", "user.html", request.META['HTTP_USER_AGENT'])
		return super(UserView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super(UserView,self).get_context_data(**kwargs)
		context["user"] = self.user
		return context


class UserTransactionsView(ListView, CategoryListMixin):
	template_name, paginate_by = None, 15

	def get(self,request,*args,**kwargs):
		self.user = request.user
		self.template_name = get_my_template("profile/transactions.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(UserTransactionsView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super(UserTransactionsView,self).get_context_data(**kwargs)
		context["user"] = self.user
		return context

	def get_queryset(self):
		return self.user.get_transactions()
