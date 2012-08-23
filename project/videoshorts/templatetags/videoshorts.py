import logging

from django import template
from django.core.urlresolvers import reverse

register = template.Library()  

logger = logging.getLogger('project.videoshorts')
    
@register.simple_tag
def chain_categories(needle, haystack):
    
    if haystack:
        category_pathing = "%s+%s" % ("+".join([t.keyname for t in haystack]), needle['keyname'])
    else:
        category_pathing = "%s" % needle['keyname']
        
    url = reverse('videoshorts-by-categories', args=[category_pathing])
    
    return url
    
@register.simple_tag
def dechain_categories(needle, haystack):
    category_pathing = "%s" % "+".join([t.keyname for t in haystack if t.id != needle['id']])
    
    if category_pathing == '':
        url = reverse('videoshorts-list')
    else:
        url = reverse('videoshorts-by-categories', args=[category_pathing])
    
    return url