from django.conf.urls.defaults import *
from tracker import views

urlpatterns = patterns('',
    url(r'^(?P<passkey>[0-9A-F]{32})/announce/$', views.announce, name='tracker_announce'),
    url(r'^(?P<passkey>[0-9A-F]{32})/scrape/$', views.scrape, name='tracker_scrape'),
)


