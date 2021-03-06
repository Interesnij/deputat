from django.conf.urls import url
from blog.view.progs import *


urlpatterns = [
    url(r'^suggest_elect_new/$', SuggestElectNew.as_view()),
    url(r'^edit_elect_new/(?P<pk>\d+)/$', EditElectNew.as_view()),
    url(r'^delete_elect_new/(?P<pk>\d+)/$', DeleteElectNew.as_view()),
    url(r'^restore_elect_new/(?P<pk>\d+)/$', RestoreElectNew.as_view()),
]
