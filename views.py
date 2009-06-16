from sitenews.models import SiteNewsItem
from django.views.generic.simple import direct_to_template


def index(request):
    d = {
        'recent_newsitems': SiteNewsItem.objects.order_by('-added')[:5],
    }
    return direct_to_template(request, 'index.html', extra_context=d)


def about(request):
    return direct_to_template(request, 'about.html')

