from django.template import Library, Node

class InboxCountNode(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        try:
            user = context['user']
            count = user.received_messages.filter(read_at__isnull=True, recipient_deleted_at__isnull=True).count()
        except (KeyError, AttributeError):
            count = '0'

        context[self.varname] = count

        return ''

def do_get_inbox_count(parser, token):
    bits = token.contents.split()

    if len(bits) != 3:
        raise TemplateSyntaxError, "get_inbox_count tag takes exactly 2 arguments"

    if bits[1] != 'as':
        raise TemplateSyntaxError, "first argument to get_latest tag must be 'as'"

    return InboxCountNode(bits[2])


register = Library()
register.tag('get_inbox_count', do_get_inbox_count)

