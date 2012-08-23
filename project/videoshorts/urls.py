from django.conf.urls.defaults import *

urlpatterns = patterns('project.videoshorts.views',
    #(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^watch/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d+)/(?P<slug>[\w/-]+)/$', 'video_from_slug', name='videoshort-by-slug'),
    url(r'^c/(?P<categories>[\w\.\-\+]+)/$', 'index', name='videoshorts-by-categories'),
    url(r'^$', 'index', name='videoshorts-list'),
)