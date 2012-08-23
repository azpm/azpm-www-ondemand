# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def chain_category_keynames(needle, haystack):
    if needle in haystack:
        category_pathing = "+".join([t for t in haystack if t != needle])
        if category_pathing == '':
            url = reverse('videoshorts-list')
        else:
            url = reverse('videoshorts-by-categories', args=[category_pathing])
        activity = u'✔'
    else:
        category_pathing = "%s+%s" % ("+".join(haystack), needle)
        url = reverse('videoshorts-by-categories', args=[category_pathing])
        activity = u'✘'
    
    return u"""<a href="%(url)s" title="%(path)s">%(activity)s</a>""" % {'url': url, 'path': category_pathing, 'activity': activity}
    