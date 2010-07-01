#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid unittests
    ~~~~~~~~~~~~~~~~~
    
    Info:
        - PyLucid initial data contains english and german pages.
    
    :copyleft: 2010 by the django-weave team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"

from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse

from pylucid_project.tests.test_tools.basetest import BaseUnittest


class ProcessManagerTest(BaseUnittest):
    """
    inherited from BaseUnittest:
        - assertPyLucidPermissionDenied()
        - initial data fixtures with default test users
        - self.login()
    """
    def _pre_setup(self, *args, **kwargs):
        super(ProcessManagerTest, self)._pre_setup(*args, **kwargs)
        self.url = reverse("SysInfo-process_manager")

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertRedirect(response, status_code=302,
            url="http://testserver/?auth=login&next_url=%s" % self.url
        )

    def test_summary(self):
        self.login("superuser")
        response = self.client.get(self.url)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                '<title>PyLucid - Process Manager</title>',
                '/usr/bin/top -bn1 -U',
                'top', 'load average:', 'PID USER',
                'proc info',
                '<li>total processes:',
                '<li>user threads:',
                '<input type="submit" value="Send signal" />',
            ),
            must_not_contain=("Traceback",)
        )







if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management
#    management.call_command('test', "pylucid_plugins.page_admin.tests.ConvertMarkupTest",
##        verbosity=0,
#        verbosity=1,
#        failfast=True
#    )
    management.call_command('test', __file__,
        verbosity=1,
#        verbosity=0,
#        failfast=True
    )
