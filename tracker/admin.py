from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from tracker.models import Peer, UserTorrentStats, UserStats

UserAdmin.fieldsets += (
    ("Tracker Extensions", { 'fields': ('passkey', ) }),
)


admin.site.register(Peer)
admin.site.register(UserTorrentStats)
admin.site.register(UserStats)
