from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.list_detail import object_detail
from sitenews.models import SiteNewsItem

urlpatterns = patterns('',
    url(r'^(?P<object_id>\d+)/view/$',
        login_required(object_detail), {
            'queryset': SiteNewsItem.objects.all(),
        },
        name='sitenews_view'),
)


