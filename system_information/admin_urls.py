# coding: utf-8

"""
    PyLucid admin url patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author:$

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, url

from system_information.admin_views import process_manager, system_info

urlpatterns = patterns('',
    url(r'^system_info/$', system_info.system_info, name='SysInfo-system_info'),
    url(r'^process_manager/$', process_manager.process_manager, name='SysInfo-process_manager'),
    url(r'^process_manager/os_abort/$', process_manager.os_abort, name='SysInfo-os_abort'),
    url(r'^process_manager/killall/$', process_manager.killall, name='SysInfo-killall'),
)
