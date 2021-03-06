from django.conf.urls.defaults import *
import views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^samplefb/', include('samplefb.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    #(r'^social/', include('django-socialregistration.socialregistration.urls')),
    (r'^fb/send/$', views.sendme),
    (r'^fb/return/$', views.returnme),
    (r'^fb/offlineaccess/$', views.offlineaccess),
    (r'^fb/show/$', views.show),
)
