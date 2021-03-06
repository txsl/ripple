from django.conf.urls import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ripple.views.home', name='home'),
    # url(r'^ripple/', include('ripple.foo.urls')),
    url(r'^$', 'rippleapp.views.index', name='index'),
    url(r'^ajax/login$', 'rippleapp.views.login', name='login'),
    url(r'^ajax/artist_events$', 'rippleapp.views.get_artist_events', name='artist_events'),
    url(r'^ajax/artist_songs$', 'rippleapp.views.get_artist_song', name='artist_songs'),
    url(r'^ajax/search$', 'rippleapp.views.search', name='search')
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
