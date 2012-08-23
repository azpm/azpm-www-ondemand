from .base import Index, Watch

video_from_slug = Watch.as_view()
index = Index.as_view()