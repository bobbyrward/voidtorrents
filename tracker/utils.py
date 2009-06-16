from django.contrib.auth.models import User
from tracker.models import UserStats


def get_user_stats(user):
    return UserStats.objects.get_or_create(user=user)


def get_torrent_stats(user, torrent):
    return UserTorrentStats.objects.get_or_create(user=user, torrent=torrent)


def get_object_or_none(klass, *args, **kwargs):
    try:
        return klass._default_manager.get(*args, **kwargs)
    except klass.DoesNotExist:
        return None


