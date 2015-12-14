from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),

    url(r'^authentication/$', views.authentication_view, name='authentication'),

    url(r'^authorization/$', views.authorization_view, name='authorization'),

    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^registration/$', views.registration_view, name='registration'),

    url(r'^confirm/$', views.confirm_view, name='confirm'),

    url(r'^registration_authorization/$', views.registration_authorization_view, name='registration_authorization'),

    url(r'^(?P<section_id>[0-9]+)/$', views.section_view, name='section'),

    url(r'^(?P<section_id>[0-9]+)/(?P<topic_id>[0-9]+)/$', views.topic_view, name='topic'),

    url(r'^(?P<section_id>[0-9]+)/(?P<topic_id>[0-9]+)/submit_message/$',
        views.submit_message_view, name='submit_message'),

    url(r'^add_section/$', views.add_section_view, name='add_section'),

    url(r'^(?P<section_id>[0-9]+)/add_topic/$', views.add_topic_view, name='add_topic'),

    url(r'^user_list/$', views.user_list_view, name='user_list'),

    url(r'^delete_user/(?P<username>.+)/$', views.delete_user_view, name='delete_user'),

    url(r'^delete_section/(?P<section_id>[0-9]+)$', views.delete_section_view, name='delete_section'),

    url(r'^delete_topic/(?P<section_id>[0-9]+)/(?P<topic_id>[0-9]+)$', views.delete_topic_view, name='delete_topic'),

    url(r'^delete_message/(?P<section_id>[0-9]+)/(?P<topic_id>[0-9]+)/(?P<message_id>[0-9]+)$',
        views.delete_message_view, name='delete_message'),

    url(r'^modification_date/(?P<topic_id>[0-9]+)$', views.modification_date_view, name='modification_date')
]