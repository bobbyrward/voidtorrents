from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from django.views.generic.simple import redirect_to
from django.contrib import admin
from forum import views as forum_views
from messages import views as messages_views

admin.autodiscover()


from sitenews.models import SiteNewsItem
import views


urlpatterns = patterns('',
    # Example:
    # (r'^voidtorrents/', include('voidtorrents.foo.urls')),

    url(r'^$', login_required(views.index), name='index'),
    url(r'^about/$', login_required(views.about), name='about'),
    url(r'^accounts/logout/$', login_required(logout_then_login), name='account_logout'),

    url(r'^forum/$', login_required(forum_views.forums_list), name='forum_index'),
    url(r'^forum/thread/(?P<thread>[0-9]+)/$', login_required(forum_views.thread), name='forum_view_thread'),
    url(r'^forum/thread/(?P<thread>[0-9]+)/reply/$', login_required(forum_views.reply), name='forum_reply_thread'),
    url(r'^forum/subscriptions/$', login_required(forum_views.updatesubs), name='forum_subscriptions'),
    url(r'^forum/(?P<slug>[-\w]+)/$', login_required(forum_views.forum), name='forum_thread_list'),
    url(r'^forum/(?P<forum>[-\w]+)/new/$', login_required(forum_views.newthread), name='forum_new_thread'),
    url(r'^forum/([-\w/]+/)(?P<forum>[-\w]+)/new/$', login_required(forum_views.newthread)),
    url(r'^forum/([-\w/]+/)(?P<slug>[-\w]+)/$', login_required(forum_views.forum), name='forum_subforum_thread_list'),

    (r'^news/', include('sitenews.urls')),
    (r'^torrents/', include('torrents.urls')),
    (r'^tracker/', include('tracker.urls')),
    (r'^accounts/', include('registration.urls')),

    url(r'^messages/$', login_required(redirect_to), {'url': 'inbox/'}),
    url(r'^messages/inbox/$', login_required(messages_views.inbox), name='messages_inbox'),
    url(r'^messages/outbox/$', login_required(messages_views.outbox), name='messages_outbox'),
    url(r'^messages/compose/$', login_required(messages_views.compose), name='messages_compose'),
    url(r'^messages/compose/(?P<recipient>[\+\w]+)/$', login_required(messages_views.compose), name='messages_compose_to'),
    url(r'^messages/reply/(?P<message_id>[\d]+)/$', login_required(messages_views.reply), name='messages_reply'),
    url(r'^messages/view/(?P<message_id>[\d]+)/$', login_required(messages_views.view), name='messages_detail'),
    url(r'^messages/delete/(?P<message_id>[\d]+)/$', login_required(messages_views.delete), name='messages_delete'),
    url(r'^messages/undelete/(?P<message_id>[\d]+)/$', login_required(messages_views.undelete), name='messages_undelete'),
    url(r'^messages/trash/$', login_required(messages_views.trash), name='messages_trash'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

