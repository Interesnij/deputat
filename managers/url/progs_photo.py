from django.conf.urls import url
from managers.view.photo import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^add_admin/(?P<pk>\d+)/$', login_required(PhotoAdminCreate.as_view())),
    url(r'^delete_admin/(?P<pk>\d+)/$', login_required(PhotoAdminDelete.as_view())),
    url(r'^add_moderator/(?P<pk>\d+)/$', login_required(PhotoModerCreate.as_view())),
    url(r'^delete_moderator/(?P<pk>\d+)/$', login_required(PhotoModerDelete.as_view())),
    url(r'^add_editor/(?P<pk>\d+)/$', login_required(PhotoEditorCreate.as_view())),
    url(r'^delete_editor/(?P<pk>\d+)/$', login_required(PhotoEditorDelete.as_view())),

    url(r'^add_worker_admin/(?P<pk>\d+)/$', login_required(PhotoWorkerAdminCreate.as_view())),
    url(r'^delete_worker_admin/(?P<pk>\d+)/$', login_required(PhotoWorkerAdminDelete.as_view())),
    url(r'^add_worker_moderator/(?P<pk>\d+)/$', login_required(PhotoWorkerModerCreate.as_view())),
    url(r'^delete_worker_moderator/(?P<pk>\d+)/$', login_required(PhotoWorkerModerDelete.as_view())),
    url(r'^add_worker_editor/(?P<pk>\d+)/$', login_required(PhotoWorkerEditorCreate.as_view())),
    url(r'^delete_worker_editor/(?P<pk>\d+)/$', login_required(PhotoWorkerEditorDelete.as_view())),

    url(r'^create_close/(?P<uuid>[0-9a-f-]+)/$', login_required(PhotoCloseCreate.as_view())),
    url(r'^delete_close/(?P<uuid>[0-9a-f-]+)/$', login_required(PhotoCloseDelete.as_view())),
    url(r'^create_rejected/(?P<uuid>[0-9a-f-]+)/$', login_required(PhotoRejectedCreate.as_view())),
    url(r'^create_claim/(?P<uuid>[0-9a-f-]+)/$', login_required(PhotoClaimCreate.as_view())),
    url(r'^unverify/(?P<photo_uuid>[0-9a-f-]+)/(?P<obj_pk>\d+)/$', login_required(PhotoUnverify.as_view())),
]