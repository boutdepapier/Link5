from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import oembed
oembed.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'link5app.views.home', name='home'),
    url(r'^(?P<page>\d+)/$', 'link5app.views.home', name='home_nav'),
    url(r'^link/$', 'link5app.views.home', name='postlink'),
    url(r'^link/load/(?P<link_id>\d+)/$', 'link5app.views.linkpreview', name='linkload'),
    url(r'^link/delete/(?P<link_id>\d+)/$', 'link5app.views.linkdelete', name='linkdelete'),
    url(r'^link/vote/(?P<link_id>\d+)/(?P<vote>[0,1]{1})/$', 'link5app.views.vote', name='vote'),

    url(r'^day/$', 'link5app.views.linkday', name='link_day'),
    url(r'^day/(?P<page>\d+)/$', 'link5app.views.linkday', name='Link_day_nav'),
    
    url(r'^week/$', 'link5app.views.linkweek', name='link_week'),
    url(r'^week/(?P<page>\d+)/$', 'link5app.views.linkweek', name='link_week_nav'),
    
    url(r'^month/$', 'link5app.views.linkmonth', name='link_month'),
    url(r'^month/(?P<page>\d+)/$', 'link5app.views.linkmonth', name='link_month_nav'),
    
    url(r'^category/(?P<slug>\w+)/$', 'link5app.views.home', name='category'),
    url(r'^category/(?P<slug>\w+)/(?P<page>\d+)/$', 'link5app.views.home', name='category_nav'),
    
    url(r'^user/edit/$', 'link5app.views.profiledit', name='profiledit'),
    
    url(r'^user/links/$', 'link5app.views.userlinks', name='user_links'),
    url(r'^user/links/(?P<page>\d+)/$', 'link5app.views.userlinks', name='user_links_nav'),
    
    url(r'^user/(?P<user_name>[^/]+)/$', 'link5app.views.home', name='user_home'),
    url(r'^user/(?P<user_name>[^/]+)/(?P<page>\d+)/$', 'link5app.views.home', name='user_nav'),
    
    url(r'^follow/(?P<user_id>\d+)/(?P<status>[0,1]{1})/$', 'link5app.views.follow', name='follow'),
    
    url(r'^comment/save/(?P<link_id>\d+)/$', 'link5app.views.commentsave', name='commentsave'),
    url(r'^comment/delete/(?P<comment_id>\d+)/$', 'link5app.views.commentdelete', name='commentdelete'),
    
    url(r'^extracting/$', 'link5app.views.getcontent', name="getcontent"),
    url(r'^login/$', 'link5app.views.login', name="login"),
    url(r'^logout/$', 'link5app.views.logout', name="logout"),
    
    url(r'^contact/$', 'link5app.views.contact', name="contact"),
    
    # Langage selection
    (r'^i18n/', include('django.conf.urls.i18n')),

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
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
    )