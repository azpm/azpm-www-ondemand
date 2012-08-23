import logging
from datetime import date

from django.core.cache import cache
from django.db.models import  Q
from django.conf import settings
from django.http import Http404
from django.views.generic import ListView, DetailView

from libscampi.contrib.cms.communism.models import Javascript, StyleSheet
from libscampi.contrib.cms.communism.views.mixins import html_link_refs
from libscampi.contrib.cms.views.base import PageNoView
from libscampi.contrib.cms.communism.models import Theme
from libscampi.contrib.cms.newsengine.models import Publish

from .mixins import CategoryMixin

logger = logging.getLogger('project.videoshorts')

class OndemandPage(PageNoView):
    base_title = u"Video On Demand"
    cached_css_key = "ondemand:vs:css"
    cached_js_key = "ondemand:vs:js"

    allow_empty = True
    model = Publish
    paginate_by = 18
    
    #the static files intensifier css for videoshorts
    videoshorts_css = {
        'url': "%sintensifier/css/videoshorts.css" % settings.STATIC_URL,
        'media': "screen", 
        'for_ie': False
    }

    def get_static_styles(self):
        return [self.videoshorts_css]

    def get_theme(self):
        try:
            theme = Theme.objects.get(keyname="intensifier")
        except Theme.DoesNotExist:
            theme = Theme.objects.none()
            
        return theme
        
    def get_page_title(self):
        return self.base_title

    
class Index(CategoryMixin, OndemandPage, ListView):    
    template_name = "videoshorts/index.html"
    
class Watch(OndemandPage, DetailView):
    template_name = "videoshorts/videoshort.html"

    def get_object(self, queryset = None, **kwargs):
        #process date
        try:
            year, month, day, slug = self.kwargs['year'], self.kwargs['month'], self.kwargs['day'], self.kwargs['slug']
        except (ValueError, KeyError):
            raise Http404("Invalid Arguments")
        else:    
            try:
                start =  date(int(year), int(month), int(day))  
            except (TypeError, ValueError):
                logger.warning("Watch.get_object received invalid arguments, %s" % kwargs)
                raise Http404
            else:
                if start > date.today():
                    raise Http404("Sorry, you can't watch things in the future!")

        try:
            obj = self.model.objects.get(start__year = start.year, start__month=start.month, start__day=start.day, slug=slug, category__keyname = "video-segment")
        except self.model.DoesNotExist:
            raise Http404("Video Short not found")

        return obj

    def get_stylesheets(self):
        publish = self.object
        story = publish.story
        article = story.article
        theme = self.get_theme()

        #try to get the cached css for this published story
        cached_css_key = 'ondemand:publish:css:%s' % (publish.id)
        if self.request.GET.get('refresh_cache', False):
            #invalidate on refresh_cache
            cache.delete(cached_css_key)
        styles = cache.get(cached_css_key, None)

        #cache empty, get the styles and refill the cache
        if not styles:
            logger.debug("missed css cache on %s" % cached_css_key)

            playlist_filters = Q(base = True)

            if story.video_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)

            if story.image_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)

            if story.audio_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)

            if story.document_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)

            if story.object_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)

            styles = StyleSheet.objects.filter(active=True, theme__id=theme.id).filter(
                #playlist finders
                playlist_filters |
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=list(article.video_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__imagetype__image__id__in=list(article.image_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__audiotype__audio__id__in=list(article.audio_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__documenttype__document__id__in=list(article.document_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__objecttype__object__id__in=list(article.object_inlines.values_list('id', flat=True)))
            ).order_by('precedence')
            cache.set(cached_css_key, styles, 60*10)

        #build a simple collection of styles
        css_collection = html_link_refs()
        for style in styles:
            css_collection.add(style)

        return css_collection

    def get_javascripts(self):
        publish = self.object
        story = publish.story
        article = story.article
        theme = self.get_theme()

        #try to get the cached javascript for this published story
        cached_scripts_key = 'ondemand:publish:js:%s' % (publish.id)
        if self.request.GET.get('refresh_cache', False):
            #invalidate on refresh_cache
            cache.delete(cached_scripts_key)
        script_ids = cache.get(cached_scripts_key, None)

        #cache empty, get the scripts and refill the cache
        if not script_ids:
            logger.debug("missed css cache on %s" % cached_scripts_key)

            playlist_filters = Q(base = True)

            if story.video_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__videoplaylist__pk = story.video_playlist_id)

            if story.image_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__imageplaylist__pk = story.image_playlist_id)

            if story.audio_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__audioplaylist__pk = story.audio_playlist_id)

            if story.document_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__documentplaylist__pk = story.document_playlist_id)

            if story.object_playlist:
                playlist_filters |= Q(mediaplaylisttemplate__objectplaylist__pk = story.object_playlist_id)

            scripts = Javascript.objects.filter(active=True, theme__id=theme.id).filter(
                playlist_filters |
                #inline finders
                Q(mediainlinetemplate__videotype__video__id__in=list(article.video_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__imagetype__image__id__in=list(article.image_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__audiotype__audio__id__in=list(article.audio_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__documenttype__document__id__in=list(article.document_inlines.values_list('id', flat=True))) |
                Q(mediainlinetemplate__objecttype__object__id__in=list(article.object_inlines.values_list('id', flat=True)))
            ).order_by('precedence')
            cache.set(cached_scripts_key, list(scripts.values_list('id', flat = True)), 60*20)
        else:
            scripts = Javascript.objects.filter(id__in=script_ids).order_by('precedence')

        #build a simple collection of styles
        script_collection = html_link_refs()
        for script in scripts:
            script_collection.add(script)

        return script_collection
