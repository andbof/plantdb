from django.views.generic import TemplateView
from django.conf.urls import patterns, include, url
from django.views.generic import CreateView
from django.contrib import admin
from files.functions import FileType
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'plant.views.index'),

    url(r'^(?P<tag>[a-zA-Z0-9]{6})$', 'plant.views.render_tag'),
    url(r'^plant_(?P<num>\d+)$', 'plant.views.render_plant_by_num', name='plant'),
    url(r'^seed_(?P<num>\d+)$', 'plant.views.render_seed_by_num', name='seed'),
    url(r'^vendor_(?P<num>\d+)$', 'plant.views.render_vendor_by_num', name='vendor'),

    url(r'^associate_qr$', 'plant.views.associate_qr', name='associate_qr'),
    url(r'^make_child/(?P<parent_type>plant|seed)_(?P<parent_id>\d+)_(?P<tag>[a-zA-Z0-9]{6})$', 'plant.views.make_child', name='make_child'),

    url(r'^upload_file$', 'files.views.upload', {'filetype': FileType.GENERAL}, name='upload_file'),
    url(r'^upload_image$', 'files.views.upload', {'filetype': FileType.IMAGE}, name='upload_image'),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="login"),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^media/(?P<sha>.*)', 'files.views.download', name='download'),

    url(r'^generate_qr$', 'qr.views.generate_qr', name='generate_qr'),

    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt')),
)
