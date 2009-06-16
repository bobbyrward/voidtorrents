from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from bencode import bencode, bdecode
from struct import pack
import socket


class HttpResponseBencoded(HttpResponse):
    def __init__(self, content):
        super(HttpResponseBencoded, self).__init__(bencode(content), mimetype='text/plain')
        self['Pragma'] = 'no-cache'


class HttpResponseFailureReason(HttpResponseBencoded):
    def __init__(self, reason):
        super(HttpResponseFailureReason, self).__init__({'failure reason': reason})


class AnnounceError(Exception):
    pass


def get_compact(params):
    return params.get('compact', ['1' if getattr(settings, 'TRACKER_PREFER_COMPACT', True) else '0'])[0]


def get_num_want(params):
    val = params.get('num_want', [getattr(settings, 'TRACKER_NUM_PEERS_DEFAULT', 30)])[0]

    if val > 100:
        val = 100
    elif val < 0:
        val = getattr(settings, 'TRACKER_NUM_PEERS_DEFAULT', 30)

    return val


class HttpResponsePeers(HttpResponseBencoded):
    def __init__(self, torrent, peers, params):
        compact = get_compact(params)

        if compact == '1':
            transform_func = self.transform_peers_compact
        else:
            transform_func = self.transform_peers_dict

        super(HttpResponsePeers, self).__init__({
            'interval': getattr(settings, 'TRACKER_ANNOUNCE_INTERVAL', 1800),
            'min interval': getattr(settings, 'TRACKER_ANNOUNCE_MIN_INTERVAL', 30),
            'complete': torrent.seeders,
            'incomplete': torrent.leechers,
            'peers': transform_func(peers[:get_num_want(params)], params),
        })


    def transform_peers_compact(self, peers, params):
        def transform_peer(peer):
            ip = socket.inet_aton(peer.ip)
            port = socket.htons(peer.port)

            return pack('>4sH', socket.inet_aton(peer.ip), peer.port)

        return ''.join(map(transform_peer, peers))


    def transform_peers_dict(self, peers, params):
        def transform_peer(peer):
            d = {'ip': peer.ip, 'port': peer.port}

            if 'no_peer_id' not in params:
                d['peer id'] = peer.peer_id

            return d

        return map(transform_peer, peers)



