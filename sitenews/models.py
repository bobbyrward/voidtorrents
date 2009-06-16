from django.db import models
from django.db.models.signals import pre_save
from django.contrib.markup.templatetags.markup import textile


class SiteNewsItem(models.Model):
    title = models.CharField(max_length=128)
    body = models.TextField(blank=True)
    textile_source = models.TextField()
    added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

    class Meta:
        get_latest_by = 'added'
        ordering = ['-added']



def _convert_newsitem_source(sender, **kwargs):
    instance = kwargs['instance']
    instance.body = textile(instance.textile_source)



pre_save.connect(_convert_newsitem_source, sender=SiteNewsItem)




