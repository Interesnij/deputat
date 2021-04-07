from django.views.generic.base import TemplateView
from generic.mixins import CategoryListMixin
from common.templates import get_small_template


class SearchView(TemplateView, CategoryListMixin):
    template_name = None

    def get(self,request,*args,**kwargs):
        self.template_name = get_small_template("search/search.html", request.user, request.META['HTTP_USER_AGENT'])
        return super(SearchView,self).get(request,*args,**kwargs)
