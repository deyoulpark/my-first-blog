from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.post_list, name='post_list'),
    url(r'^post/(?P<pk>\d+)/$', views.post_detail, name='post_detail'),
    url(r'^post/new/$', views.post_new, name='post_new'),
    url(r'^post/(?P<pk>\d+)/edit/$', views.post_edit, name='post_edit'),
    url(r'^drafts/$', views.post_draft_list, name='post_draft_list'),
    url(r'^post/(?P<pk>\d+)/publish/$', views.post_publish, name='post_publish'),
    url(r'^post/(?P<pk>\d+)/remove/$', views.post_remove, name='post_remove'),
    url(r'^upfile/(?P<pk>\d+)/remove/$', views.upfile_remove, name='upfile_remove'),
    url(r'^upload/home/$', views.home, name='home'),
    #url(r'^uploads/simple/$', views.simple_upload, name='simple_upload'),
    url(r'^upload/form/$', views.model_form_upload, name='model_form_upload'),
    #url(r'^upload/', views.upload_file, name='upload_file'),
    #url(r'^uploaded$', views.uploaded, name='uploaded'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
