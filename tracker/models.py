from django.db import models
from django.contrib.auth.models import User
from torrents.models import Torrent, BigIntegerField
from uuid import uuid4


def _create_user_passkey():
    return uuid4().hex.upper()


User.add_to_class('passkey', models.CharField(max_length=32, default=_create_user_passkey))

class Peer(models.Model):
    user = models.ForeignKey(User)
    torrent = models.ForeignKey(Torrent)
    ip = models.IPAddressField()
    port = models.IntegerField()
    peer_id = models.CharField(max_length=40)
    last_action = models.DateTimeField(auto_now=True)
    started = models.DateTimeField(auto_now_add=True)
    left = BigIntegerField()
    downloaded = BigIntegerField(default=0)
    uploaded = BigIntegerField(default=0)
    client = models.CharField(max_length=128)
    connectable = models.BooleanField(default=False)

    def __unicode__(self):
        return 'user=%s torrent=%s' % (self.user.username, self.torrent.name)


class UserTorrentStats(models.Model):
    user = models.ForeignKey(User)
    torrent = models.ForeignKey(Torrent)
    finished = models.BooleanField(default=False)
    uploaded = BigIntegerField(default=0)
    downloaded = BigIntegerField(default=0)
    left = BigIntegerField(default=0)
    last_action = models.DateTimeField(auto_now=True)
    when_started = models.DateTimeField(auto_now_add=True)
    when_completed = models.DateTimeField(blank=True)

    def __unicode__(self):
        return 'user=%s torrent=%s' % (self.user.username, self.torrent.name)


class UserStats(models.Model):
    user = models.ForeignKey(User, unique=True)
    uploaded = BigIntegerField(default=0)
    downloaded = BigIntegerField(default=0)

    def ratio(self):
      if self.uploaded == 0 or self.downloaded == 0:
        return 0
      else:
        return float(self.uploaded) / float(self.downloaded)

    def __unicode__(self):
        return self.user.username


