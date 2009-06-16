from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect, HttpResponse
from torrents.forms import UploadForm
from torrents.models import Torrent
from bencode import bdecode, bencode
from django.core.urlresolvers import reverse
import logging


log = logging.getLogger(__name__)



def upload(request):
    log.debug('TEsting')

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            torrent = form.save(commit=False)
            torrent.process_bdecoded_data(request.FILES['torrent_file'].name, form.cleaned_data['torrent_file'])
            torrent.owner = request.user
            torrent.save()

            if getattr(torrent, 'save_m2m', None):
                torrent.save_m2m()

            return HttpResponseRedirect(reverse('torrent_view', kwargs={'object_id': torrent.id}))

    else:
        form = UploadForm()

    return render_to_response('torrents/torrent_upload.html', {
            'form': form,
        })


def download(request, object_id):
    torrent = get_object_or_404(Torrent, pk=object_id)

    fd = open(torrent.torrent_file)
    d = bdecode(fd.read())
    fd.close()

    if 'announce-list' in d:
        del d['announce-list']

    d['announce'] = 'http://%s%s' % (Site.objects.get_current().domain, reverse('tracker_announce', kwargs={'passkey': request.user.passkey}))

    bencoded = bencode(d)
    response = HttpResponse(bencoded, mimetype='application/x-bittorrent')
    response['Content-Disposition'] = 'attachment; filename="%s"' % torrent.filename

    return response


