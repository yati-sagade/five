from django.conf.urls import patterns, include, url
import core.urls

urlpatterns = patterns('',
    url(r'', include(core.urls)),
)
