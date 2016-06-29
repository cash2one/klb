from django.conf.urls import patterns, include, url
import settings
import members.urls as member_urls
import klbapp.urls as app_urls
import web.urls as web_urls
import wechat.urls as wechat
import webadmin.urls as webadmin
import bxservice.urls as bx_urls
import ClientAdmin.urls as ClientAdmin_urls
import ebusiness.urls as ebusiness
from django.contrib import admin

admin.autodiscover()

handler404 = 'klbapp.views.Error_404'
handler500 = 'klbapp.views.Error_500'

urlpatterns = patterns('',
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
                       url(r'^$', 'web.views.WebIndex', name='home'),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
                       url(r'^master/', include(admin.site.urls)),
                       url(r'^fonts/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.FONTS_DIR, 'show_indexes': True}),
                       url(r'^members/', include(member_urls)),
                       url(r'^app/', include(app_urls)),
                       url(r'^web/', include(web_urls)),
                       url(r'^bxservice/', include(bx_urls)),
                       url(r'^wechat/', include(wechat)),
                       url(r'^ClientAdmin/', include(ClientAdmin_urls)),
                       url(r'^webadmin/', include(webadmin)),
                       url(r'^ebusiness/', include(ebusiness)),
                       url(r'^PayCallback/$', 'bxservice.views.PayCallback', name="PayCallback"),
                       url(r'^PayCallback/(?P<a>\w+)/$', 'bxservice.views.PayCallback', name="PayCallback"),
                       url(r'^pages/BgKlbInsurePolicy/isurePolicyBackForAs.htm','bxservice.views.PayCallback_AS'),
                       url(r'', include('tokenapi.urls')),
                       )
