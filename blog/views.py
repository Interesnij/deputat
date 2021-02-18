import re
import json
MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)
from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin
from blog.models import *
from blog.forms import BlogCommentForm
from stst.models import BlogNumbers
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from django.http import Http404
from django.views.generic import ListView
from common.utils import get_small_template, get_full_template


class BlogDetailView(TemplateView, CategoryListMixin):
	template_name = None

	def get(self,request,*args,**kwargs):
		self.blog = Blog.objects.get(pk=self.kwargs["pk"])
		if request.user.is_authenticated:
			current_pk = request.user.pk
		else:
			current_pk = 0
		if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
			BlogNumbers.objects.create(user=current_pk, blog=self.blog.pk, platform=0)
		else:
			BlogNumbers.objects.create(user=current_pk, blog=self.blog.pk, platform=1)
		self.template_name = get_full_template("blog/blog.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(BlogDetailView,self).get(request,*args,**kwargs)

	def get_context_data(self,**kwargs):
		context=super(BlogDetailView,self).get_context_data(**kwargs)
		context["object"] = self.blog
		return context


class AllElectsNewsView(ListView, CategoryListMixin):
	template_name, tag, paginate_by = None, '', 12

	def get(self,request,*args,**kwargs):
		self.template_name = get_small_template("blog/elect_news.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(AllElectsNewsView,self).get(request,*args,**kwargs)

	def get_queryset(self):
		if self.tag:
			return ElectNew.objects.filter(tags__name=self.tag)
		else:
			return ElectNew.objects.only("pk")

	def get_context_data(self, **kwargs):
		context = super(AllElectsNewsView, self).get_context_data(**kwargs)
		context['tag'] = self.tag
		return context


class ProectNewsView(ListView, CategoryListMixin):
	template_name = "blog/blog_news.html"
	paginate_by = 12

	def get(self,request,*args,**kwargs):
		self.template_name = get_small_template("blog/blog_news.html", request.user, request.META['HTTP_USER_AGENT'])
		return super(ProectNewsView,self).get(request,*args,**kwargs)

	def get_queryset(self):
		blog_news = Blog.objects.only("pk")
		return blog_news


class BlogCommentList(ListView):
    template_name = "blog_comments.html"
    paginate_by = 15

    def get(self,request,*args,**kwargs):
	    self.blog = Blog.objects.get(pk=self.kwargs["pk"])
	    return super(BlogCommentList,self).get(request,*args,**kwargs)
    def get_context_data(self, **kwargs):
	    context = super(BlogCommentList, self).get_context_data(**kwargs)
	    context['parent'] = self.blog
	    return context

    def get_queryset(self):
	    comments = self.blog.get_comments()
	    return comments


class BlogCommentCreate(View):

    def post(self,request,*args,**kwargs):
        form_post = BlogCommentForm(request.POST)
        blog_comment = Blog.objects.get(pk=request.POST.get('pk'))

        if request.is_ajax() and form_post.is_valid() and blog_comment.comments_enabled:
            comment = form_post.save(commit=False)
            new_comment = comment.create_comment(commenter=request.user, parent_comment=None, blog_comment=blog_comment, text=comment.text)
            return render(request, 'parent.html',{'comment': new_comment})
        else:
            return HttpResponseBadRequest()


class BlogReplyCreate(View):
    def post(self,request,*args,**kwargs):
        form_post = BlogCommentForm(request.POST)
        parent = BlogComment.objects.get(pk=request.POST.get('post_comment'))

        if request.is_ajax() and form_post.is_valid():
            comment = form_post.save(commit=False)
            new_comment = comment.create_comment(commenter=request.user, parent_comment=parent, blog_comment=None, text=comment.text)
            return render(request, 'blog_reply.html',{'reply': new_comment, 'comment': parent,})
        else:
            return HttpResponseBadRequest()

class BlogCommentDelete(View):
    def get(self,request,*args,**kwargs):
        comment = BlogComment.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.pk == comment.commenter.pk:
            comment.is_deleted = True
            comment.save(update_fields=['is_deleted'])
            return HttpResponse()
        else:
            raise Http404

class BlogCommentAbortDelete(View):
    def get(self,request,*args,**kwargs):
        comment = BlogComment.objects.get(pk=self.kwargs["pk"])
        if request.is_ajax() and request.user.pk == comment.commenter.pk:
            comment.is_deleted = False
            comment.save(update_fields=['is_deleted'])
            return HttpResponse()
        else:
            raise Http404


class BlogLikeCreate(View):
    def get(self, request, **kwargs):
        blog = Blog.objects.get(pk=self.kwargs["pk"])
        if not request.is_ajax() and not blog.votes_on:
            raise Http404
        try:
            likedislike = BlogVotes.objects.get(parent=blog, user=request.user)
            if likedislike.vote is not BlogVotes.LIKE:
                likedislike.vote = BlogVotes.LIKE
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                likedislike.delete()
                result = False
        except BlogVotes.DoesNotExist:
            BlogVotes.objects.create(parent=blog, user=request.user, vote=BlogVotes.LIKE)
            result = True
        likes, dislikes = blog.likes_count(), blog.dislikes_count()
        if likes != 0:
            like_count = likes
        else:
            like_count = ""
        if dislikes != 0:
            dislike_count = dislikes
        else:
            dislike_count = ""
        return HttpResponse(json.dumps({"result": result,"like_count": str(like_count),"dislike_count": str(dislike_count)}),content_type="application/json")


class BlogCommentLikeCreate(View):
    def get(self, request, **kwargs):
        comment = BlogComment.objects.get(pk=self.kwargs["comment_pk"])
        if not request.is_ajax():
            raise Http404
        try:
            likedislike = BlogCommentVotes.objects.get(item=comment, user=request.user)
            if likedislike.vote is not BlogCommentVotes.LIKE:
                likedislike.vote = BlogCommentVotes.LIKE
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                likedislike.delete()
                result = False
        except BlogCommentVotes.DoesNotExist:
            BlogCommentVotes.objects.create(item=comment, user=request.user, vote=BlogCommentVotes.LIKE)
            result = True
        likes = comment.likes_count()
        if likes != 0:
            like_count = likes
        else:
            like_count = ""
        dislikes = comment.dislikes_count()
        if dislikes != 0:
            dislike_count = dislikes
        else:
            dislike_count = ""
        return HttpResponse(json.dumps({"result": result,"like_count": str(like_count),"dislike_count": str(dislike_count)}),content_type="application/json")


class BlogDislikeCreate(View):
    def get(self, request, **kwargs):
        blog = Blog.objects.get(pk=self.kwargs["pk"])
        if not request.is_ajax() and not blog.votes_on:
            raise Http404
        try:
            likedislike = BlogVotes.objects.get(parent=blog, user=request.user)
            if likedislike.vote is not BlogVotes.DISLIKE:
                likedislike.vote = BlogVotes.DISLIKE
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                likedislike.delete()
                result = False
        except BlogVotes.DoesNotExist:
            BlogVotes.objects.create(parent=blog, user=request.user, vote=BlogVotes.DISLIKE)
            result = True
        likes = blog.likes_count()
        if likes != 0:
            like_count = likes
        else:
            like_count = ""
        dislikes = blog.dislikes_count()
        if dislikes != 0:
            dislike_count = dislikes
        else:
            dislike_count = ""
        return HttpResponse(json.dumps({"result": result,"like_count": str(like_count),"dislike_count": str(dislike_count)}),content_type="application/json")


class BlogCommentDislikeCreate(View):
    def get(self, request, **kwargs):
        comment = BlogComment.objects.get(pk=self.kwargs["comment_pk"])
        if not request.is_ajax():
            raise Http404
        try:
            likedislike = BlogCommentVotes.objects.get(item=comment, user=request.user)
            if likedislike.vote is not BlogCommentVotes.DISLIKE:
                likedislike.vote = BlogCommentVotes.DISLIKE
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                likedislike.delete()
                result = False
        except BlogCommentVotes.DoesNotExist:
            BlogCommentVotes.objects.create(item=comment, user=request.user, vote=BlogCommentVotes.DISLIKE)
            result = True
        likes = comment.likes_count()
        if likes:
            like_count = likes
        else:
            like_count = ""
        dislikes = comment.dislikes_count()
        if dislikes != 0:
            dislike_count = dislikes
        else:
            dislike_count = ""
        return HttpResponse(json.dumps({"result": result,"like_count": str(like_count),"dislike_count": str(dislike_count)}),content_type="application/json")
