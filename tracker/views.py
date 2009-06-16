# Create your views here.
from tracker.utils import get_object_or_none
from tracker.http import HttpResponseBencoded, HttpResponseFailureReason, AnnounceError, HttpResponsePeers
from tracker.models import Peer, UserTorrentStats
from torrents.models import Torrent
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.models import User
from django.conf import settings
from bencode import bencode, bdecode
from cgi import parse_qs
from binascii import b2a_hex
from datetime import datetime
import logging
import socket


#log = logging.getLogger(__name__)


def get_ip(request, params):
    if 'HTTP_X_REAL_IP' in request.META:
        return request.META['HTTP_X_REAL_IP']
    else:
        return request.META['REMOTE_ADDR']


def announce_started(request, user, connectable, params, torrent, peer_id, peer_self):
    if peer_self:
        raise AnnounceError('Already started.')

    p = Peer()
    p.user = user
    p.torrent = torrent
    p.ip = get_ip(request, params)
    p.port = int(params['port'][0])
    p.peer_id = peer_id
    p.left = int(params['left'][0])
    p.downloaded = 0
    p.uploaded = 0
    p.client = request.META['HTTP_USER_AGENT']
    p.connectable = connectable
    p.save()

    left = long(params['left'][0])

    stats = UserTorrentStats.get_or_create(user=user, torrent=torrent)[0]
    stats.left = left

    if left == 0:
        stats.finished = True

    stats.save()


    if p.left == 0:
        torrent.seeders = torrent.seeders + 1
    else:
        torrent.leechers = torrent.leechers + 1

    torrent.last_action = datetime.now()
    torrent.save()

    return HttpResponsePeers(torrent, Peer.objects.filter(torrent=torrent).order_by('?'), params)


def announce_stopped(request, user, connectable, params, torrent, peer_id, peer_self):
    if not peer_self:
        raise AnnounceError('Broken client. Never started')

    if peer_self.left == 0:
        torrent.seeders = torrent.seeders - 1
    else:
        torrent.leechers = torrent.leechers - 1

    torrent.last_action = datetime.now()
    torrent.save()

    left = long(params['left'][0])
    uploaded = long(params['uploaded'][0])
    downloaded = long(params['downloaded'][0])

    uploaded_delta = uploaded - peer_self.uploaded
    downloaded_delta = downloaded - peer_self.downloaded

    userstats = UserStats.get_or_create(user=user)[0]
    userstats.uploaded += uploaded_delta
    userstats.downloaded += downloaded_delta
    userstats.save()

    stats = UserTorrentStats.get_or_create(user=user, torrent=torrent)[0]
    stats.uploaded += uploaded_delta
    stats.downloaded += downloaded_delta
    stats.left = left

    if left == 0:
        stats.finished = True

    stats.save()

    peer_self.delete()

    # return a list of peers on STOPPED?? stupid
    return HttpResponsePeers(torrent, Peer.objects.filter(torrent=torrent).order_by('?'), params)


def announce_completed(request, user, connectable, params, torrent, peer_id, peer_self):
    if not peer_self:
        raise AnnounceError('Broken client. Never started')

    torrent.seeders += 1
    torrent.leechers += 1
    torrent.times_completed += 1
    torrent.last_action = datetime.now()
    torrent.save()

    stats = UserTorrentStats.get(user=user, torrent=torrent)
    stats.when_completed = datetime.now()
    stats.save()

    return announce_poll(request, user, connectable, params, torrent, peer_id, peer_self)


def announce_poll(request, user, connectable, params, torrent, peer_id, peer_self):
    if not peer_self:
        raise AnnounceError('Broken client. Never started')

    left = long(params['left'][0])
    uploaded = long(params['uploaded'][0])
    downloaded = long(params['downloaded'][0])

    uploaded_delta = uploaded - peer_self.uploaded
    downloaded_delta = downloaded - peer_self.downloaded

    stats = UserTorrentStats.get_or_create(user=user, torrent=torrent)[0]
    stats.uploaded += uploaded_delta
    stats.downloaded += downloaded_delta
    stats.left = left

    if left == 0:
        stats.finished = True

    stats.save()

    userstats = UserStats.get_or_create(user=user)[0]
    userstats.uploaded += uploaded_delta
    userstats.downloaded += downloaded_delta
    userstats.save()

    peer_self.left = long(params['left'][0])
    peer_self.downloaded = long(params['downloaded'][0])
    peer_self.uploaded = long(params['uploaded'][0])
    peer_self.ip = get_ip(request, params)
    peer_self.port = int(params['port'][0])
    peer_self.peer_id = peer_id
    peer_self.client = request.META['HTTP_USER_AGENT']
    peer_self.connectable = connectable
    peer_self.save()

    torrent.last_action = datetime.now()
    torrent.save()

    return HttpResponsePeers(torrent, Peer.objects.filter(torrent=torrent).exclude(user=user).order_by('?'), params)


"""
Checks to perform...
    Disallow browser user agents?
    limit leeching to 1 per ip
    check for banned client
    ratio check?
    update peer stats
    update user stats
    update torrent last action
"""


def announce(request, passkey):
    try:
        # First off find the user by passkey
        user = get_object_or_none(User, passkey=passkey)

        if not user:
            raise AnnounceError('Invalid passkey')

        #TODO: Make sure they're authorized

        # parse the query string manually
        get_params = parse_qs(request.META['QUERY_STRING'])

        def hash_param(name):
            try:
                val = b2a_hex(get_params[name][0])

                if len(val) != 40:
                    raise Exception()

            except Exception, e:
                raise AnnounceError('Invalid %s' % name)

            return val

        # verify required hash params
        info_hash = hash_param('info_hash').upper()
        peer_id = hash_param('peer_id')

        for param_name in ('port', 'uploaded', 'downloaded', 'left',):
            if param_name not in get_params:
                raise AnnounceError('Required parameter "%s" missing' % param_name)

        port = int(get_params['port'][0])
        if port <= 0 or port > 65535:
            raise AnnounceError('Invalid port')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)

        try:
            s.connect((get_ip(), port))
        except Exception:
            connectable = False
        else:
            connectable = True
        finally:
            s.close()


        try:
            torrent = Torrent.objects.get(info_hash=info_hash)
        except Torrent.DoesNotExist:
            raise AnnounceError('Torrent not found')

        left = long(get_params['left'][0])

        if left < 0 or left > torrent.filesize:
            raise AnnounceError('Invalid left')

        event = get_params.get('event', ['poll'])[0]

        try:
            peer_self = Peer.objects.get(user=user, torrent=torrent)
        except Peer.DoesNotExist:
            peer_self = None

        try:
            dispatch = {
                'started': announce_started,
                'stopped': announce_stopped,
                'completed': announce_completed,
                'poll': announce_poll,
            }[event]

        except KeyError:
            raise AnnounceError('Invalid event param')

        return dispatch(request, user, connectable, get_params, torrent, peer_id, peer_self)
    except AnnounceError, e:
        return HttpResponseFailureReason(e.message)

    return HttpResponseFailureReason('Impossible to get here?')


def scrape(request, passkey):
    return HttpResponseNotFound()



