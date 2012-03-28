from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from filebrowser.sites import site

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import oembed
oembed.autodiscover()

import link5app
from link5app import forms

urlpatterns = patterns('',
    url(r'^$', 'link5app.views.home', name='home'),
    url(r'^link/page/(?P<page>\d+)/$', 'link5app.views.home', name='home_nav'),
    url(r'^link/$', 'link5app.views.home', name='postlink'),
    url(r'^link/load/(?P<link_id>[^/]+)/$', 'link5app.views.linkpreviewredirect', name='linkredirect'),
    url(r'^link/delete/(?P<link_id>\w+)/$', 'link5app.views.linkdelete', name='linkdelete'),
    url(r'^link/vote/(?P<link_id>\w+)/(?P<vote>[0,1]{1})/$', 'link5app.views.vote', name='vote'),

    url(r'^top/day/$', 'link5app.views.linkday', name='link_day'),
    url(r'^top/day/(?P<page>\d+)/$', 'link5app.views.linkday', name='Link_day_nav'),
    
    url(r'^top/week/$', 'link5app.views.linkweek', name='link_week'),
    url(r'^top/week/(?P<page>\d+)/$', 'link5app.views.linkweek', name='link_week_nav'),
    
    url(r'^top/month/$', 'link5app.views.linkmonth', name='link_month'),
    url(r'^top/month/(?P<page>\d+)/$', 'link5app.views.linkmonth', name='link_month_nav'),
    
    url(r'^category/(?P<category>\w+)/$', 'link5app.views.home', name='category'),
    url(r'^category/(?P<category>\w+)/(?P<page>\d+)/$', 'link5app.views.home', name='category_nav'),
    
    url(r'^user/edit/to/(?P<page>\d+)/$', 'link5app.views.profiledit', name='profiledit_to_nav'),
    url(r'^user/edit/from/(?P<page>\d+)/$', 'link5app.views.profiledit', name='profiledit_from_nav'),
    url(r'^user/info/(?P<user_name>[^/]+)/$', 'link5app.views.profiledit', name='user_view'),
    url(r'^user/info/(?P<user_name>[^/]+)/(?P<page>\d+)/$', 'link5app.views.profiledit', name='user_view_nav'),
    
    url(r'^following/links/$', 'link5app.views.userlinks', name='user_links'),
    url(r'^following/links/(?P<page>\d+)/$', 'link5app.views.userlinks', name='user_links_nav'),
    
    url(r'^user/(?P<user_name>[^/]+)/$', 'link5app.views.home', name='user_home'),
    url(r'^user/(?P<user_name>[^/]+)/(?P<page>\d+)/$', 'link5app.views.home', name='user_nav'),
    
    url(r'^follow/(?P<user_id>\d+)/(?P<status>[0,1]{1})/$', 'link5app.views.follow', name='follow'),
    
    url(r'^comment/save/(?P<link_id>\d+)/$', 'link5app.views.commentsave', name='commentsave'),
    url(r'^comment/delete/(?P<link_id>\d+)/(?P<comment_id>\d+)/$', 'link5app.views.commentdelete', name='commentdelete'),
    url(r'^comment/open/(?P<link_id>\d+)/$', 'link5app.views.home', name='commentopen'),
    
    url(r'^url/extracting/$', 'link5app.views.getcontent', name="getcontent"),
    url(r'^auth/login/$', 'link5app.views.login', name="login"),
    url(r'^auth/logout/$', 'link5app.views.logout', name="logout"),
    
    url(r'^me/contact/$', 'link5app.views.contact', name="contact"),
    
    url(r'^login/password_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', name="pass_form_reset"),
    url(r'^login/password_reset/$', 'django.contrib.auth.views.password_reset',{'password_reset_form': link5app.forms.PasswordResetForm}),
    url(r'^login/', include('django.contrib.auth.urls')),
    
    # Langage selection
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    (r'^admin/', include(admin.site.urls)),
    
    url(r'^(?P<link_id>[^/]+)/(?P<title_url>[^/]+)/$', 'link5app.views.linkpreview', name='linkload'),
    url(r'^(?P<link_id>[^/]+)/$', 'link5app.views.linkpreview', name='linkload_short'),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns = patterns('',
        url(r'^admin/rosetta/', include('rosetta.urls')),
    ) + urlpatterns

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
    )

