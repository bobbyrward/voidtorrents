DOMAIN = 'voidtorrents.mma-hq.com'
ALLDIRS = [
    '/home/django/domains/%s/%s/lib/python2.5/site-packages' % (DOMAIN, DOMAIN),
    '/home/django/domains/%s/voidtorrents/' % DOMAIN,
    '/home/django/domains/%s/' % DOMAIN,
    ]

import os, sys, site

prev_sys_path = list(sys.path)

for directory in ALLDIRS:
    site.addsitedir(directory)

new_sys_path = []

for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)

sys.path[:0] = new_sys_path

sys.path.append('/home/django/domains/%s/personal/' % DOMAIN)

os.environ['PYTHON_EGG_CACHE'] = '/home/django/.python-eggs'
os.environ['DJANGO_SETTINGS_MODULE'] = 'voidtorrents.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
