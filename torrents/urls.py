from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_detail, object_list
from torrents.models import Torrent
from torrents import views

urlpatterns = patterns('',
    url(r'^$',
        login_required(object_list), {
            'queryset': Torrent.objects.order_by('-added'),
            'allow_empty': True,
            'paginate_by': 25,
        },
        name='torrent_list'),

    url(r'^view/(?P<object_id>\d+)/$',
        login_required(object_detail), {
            'queryset': Torrent.objects.all(),
        },
        name='torrent_view'),

    url(r'^download/(?P<object_id>\d+)/$', login_required(views.download), name='torrent_download'),
    url(r'^upload/$', login_required(views.upload), name='torrent_upload'),
)

