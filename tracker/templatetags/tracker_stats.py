from django.template import Library, Node
from tracker.models import UserTorrentStats, UserStats


class UserTrackerStatsNode(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = UserStats.objects.get_or_create(user=context['user'])[0]
        return ''


def do_get_user_tracker_stats(parser, token):
    bits = token.contents.split()

    if len(bits) != 3:
        raise TemplateSyntaxError, "get_user_tracker_stats tag takes exactly 2 arguments"

    if bits[1] != 'as':
        raise TemplateSyntaxError, "first argument to get_latest tag must be 'as'"

    return UserTrackerStatsNode(bits[2])


register = Library()
register.tag('get_user_tracker_stats', do_get_user_tracker_stats)


