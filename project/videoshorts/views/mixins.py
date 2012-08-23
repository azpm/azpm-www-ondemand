import logging
from datetime import  datetime

from django.core.cache import cache
from django.db.models import  Q
from libscampi.contrib.cms.newsengine.models import Publish, StoryCategory

logger = logging.getLogger('project.videoshorts')

class CategoryMixin(object):
    limits = None
    available_categories = None
    
    def get(self, request, *args, **kwargs):
        #keyname specified in url
        if 'c' in request.GET:
            limits = request.GET.get('c','').split(' ')
            logger.debug(limits)

            filters = [Q(keyname=value) for value in limits]
            query = filters.pop()
            # Or the Q object with the ones remaining in the list
            for filter in filters:
                query |= filter

            self.limits = StoryCategory.objects.filter(Q(browsable=True) & query)
            
        #finally return the parent get method
        return super(CategoryMixin, self).get(request, *args, **kwargs)
        
    def get_queryset(self):
        now = datetime.now()
        
        qs = Publish.active.filter(category__keyname = "video-segment").exclude(start__gte=now)
        
        cat_cache_key = "videoshort:categories"
        categories = cache.get(cat_cache_key, None)
        
        if not categories:
            categories = StoryCategory.genera.for_cloud(qs)
            cache.set(cat_cache_key, categories, 60*60)
            
        if self.limits:
            filters = [Q(story__categories__pk=value[0]) for value in self.limits.values_list('id')]
            for filter in filters:
                qs = qs.filter(filter)
                
            self.available_categories = categories.exclude(pk__in=list(self.limits.values_list('id', flat=True)))
        else:
            self.available_categories = categories
        
        return qs
        
    def get_context_data(self, *args, **kwargs):
        logger.debug("CategoryMixin.get_context_data started")
        #get the existing context
        context = super(CategoryMixin, self).get_context_data(*args, **kwargs)

        if self.limits:
            get_args = u"c=%s" % "+".join([t.keyname for t in self.limits])
        else:
            get_args = None

        #give the templat the current picker
        context.update({
            'limits': self.limits,
            'categories': self.available_categories,
            'get_args': get_args
        })
            
        return context