from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'link5app.views.home', name='home'),
    url(r'^page/(?P<page>\d+)$', 'link5app.views.home', name='home'),
    url(r'^link/$', 'link5app.views.link', name='home'),
    url(r'^link/load/(?P<link_id>\d+)$', 'link5app.views.linkpreview', name='linkpreview'),
    url(r'^link/vote/(?P<link_id>\d+)/(?P<vote>[0,1]{1})$', 'link5app.views.vote', name='vote'),
    
    url(r'^profil/edit/$', 'link5app.views.profiledit', name='profiledit'),
    
    url(r'^comment/save/(?P<link_id>\d+)$', 'link5app.views.commentsave', name='commentsave'),
    
    url(r'^extracting/$', 'link5app.views.getcontent', name="getcontent"),
    url(r'^login/$', 'link5app.views.login', name="login"),
    url(r'^logout/$', 'link5app.views.logout', name="logout"),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^grappelli/', include('grappelli.urls')),
    (r'^admin/', include(admin.site.urls)),
    
)
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns = patterns('',
        url(r'^admin/rosetta/', include('rosetta.urls')),
    ) + urlpatterns

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )