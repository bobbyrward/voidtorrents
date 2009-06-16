from django import forms
from torrents.models import Torrent
from bencode import bdecode, bencode


class UploadForm(forms.ModelForm):
    torrent_file = forms.FileField()

    class Meta:
        model = Torrent

        fields = [
            'name',
            'torrent_file',
            'description',
        ]


    def clean_torrent_file(self):
        uploaded_file = self.cleaned_data['torrent_file']

        try:
            d = bdecode(uploaded_file.read())
        except Exception:
            raise forms.ValidationError('Not a valid bencoded file')


        return d



