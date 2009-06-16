from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.core import exceptions
import os
import tagging
from hashlib import sha1
from bencode import bdecode, bencode



class BigIntegerField(models.IntegerField):
    def db_type(self):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE[:8] == 'postgres':
            return "bigint"
        else:
            raise NotImplemented

    def get_internal_type(self):
        return "BigIntegerField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(_("This value must be a long integer."))


class Torrent(models.Model):
    info_hash = models.CharField(max_length=40)
    name = models.CharField(max_length=255)
    torrent_file = models.FilePathField(path=settings.TORRENTS_UPLOAD_DIR, match=r'.*\.torrent', max_length=255)
    filename = models.CharField(max_length=255)
    description = models.TextField()
    added = models.DateTimeField(auto_now_add=True)

    filesize = BigIntegerField()
    filecount = models.IntegerField()

    seeders = models.IntegerField(default=0)
    leechers = models.IntegerField(default=0)

    times_completed = models.IntegerField(default=0)

    last_action = models.DateTimeField(blank=True)

    visible = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)

    nfo = models.TextField(blank=True)

    free_leech = models.BooleanField(default=False)
    hide_filesize = models.BooleanField(default=False)

    owner = models.ForeignKey(User)

    def process_bdecoded_data(self, name, data):
        self.filename = name
        self.info_hash = sha1(bencode(data['info'])).hexdigest().upper()
        self.filesize = reduce(lambda x, y: x + y['length'], data['info']['files'], 0)
        self.filecount = len(data['info']['files'])
        self.torrent_file = 'unknown'
        self.bdecoded_data = data
# | category        | int(10) unsigned       | NO   | MUL | 0                   |                |
# | type            | enum('single','multi') | NO   |     | single              |                |
# | owner           | int(10) unsigned       | NO   | MUL | 0                   |                |


    def __unicode__(self):
      return self.name


    class Meta:
        get_latest_by = 'added'
        ordering = ['-added']



def _write_bencoded_torrent(sender, **kwargs):
    instance = kwargs['instance']

    if getattr(instance, 'bdecoded_data', None):
        encoded = bencode(instance.bdecoded_data)
        filename = os.path.join(settings.TORRENTS_UPLOAD_DIR, '%d.torrent' % instance.id)

        fd = open(filename, 'wb')
        fd.write(encoded)
        fd.close()

        del instance.bdecoded_data

        instance.torrent_file = filename
        instance.save()


post_save.connect(_write_bencoded_torrent, sender=Torrent)
tagging.register(Torrent)

