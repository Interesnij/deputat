from django.conf.urls import url
from managers.view.video import *
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^add_admin/(?P<pk>\d+)/$', login_required(VideoAdminCreate.as_view())),
    url(r'^delete_admin/(?P<pk>\d+)/$', login_required(VideoAdminDelete.as_view())),
    url(r'^add_moderator/(?P<pk>\d+)/$', login_required(VideoModerCreate.as_view())),
    url(r'^delete_moderator/(?P<pk>\d+)/$', login_required(VideoModerDelete.as_view())),
    url(r'^add_editor/(?P<pk>\d+)/$', login_required(VideoEditorCreate.as_view())),
    url(r'^delete_editor/(?P<pk>\d+)/$', login_required(VideoEditorDelete.as_view())),

    url(r'^add_worker_admin/(?P<pk>\d+)/$', login_required(VideoWorkerAdminCreate.as_view())),
    url(r'^delete_worker_admin/(?P<pk>\d+)/$', login_required(VideoWorkerAdminDelete.as_view())),
    url(r'^add_worker_moderator/(?P<pk>\d+)/$', login_required(VideoWorkerModerCreate.as_view())),
    url(r'^delete_worker_moderator/(?P<pk>\d+)/$', login_required(VideoWorkerModerDelete.as_view())),
    url(r'^add_worker_editor/(?P<pk>\d+)/$', login_required(VideoWorkerEditorCreate.as_view())),
    url(r'^delete_worker_editor/(?P<pk>\d+)/$', login_required(VideoWorkerEditorDelete.as_view())),

    url(r'^create_close/(?P<uuid>[0-9a-f-]+)/$', login_required(VideoCloseCreate.as_view())),
    url(r'^delete_close/(?P<uuid>[0-9a-f-]+)/$', login_required(VideoCloseDelete.as_view())),
    url(r'^create_rejected/(?P<uuid>[0-9a-f-]+)/$', login_required(VideoRejectedCreate.as_view())),
    url(r'^create_claim/(?P<uuid>[0-9a-f-]+)/$', login_required(VideoClaimCreate.as_view())),
    url(r'^unverify/(?P<video_uuid>[0-9a-f-]+)/(?P<obj_pk>\d+)/$', login_required(VideoUnverify.as_view())),
]
