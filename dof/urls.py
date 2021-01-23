# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# Top level URL configuration

from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.contrib import admin
from Plein.views import site_root_view
from Beheer.views import BeheerAdminSite
from Producten.view_leveringen import DownloadView

# replace the admin site
admin.site.__class__ = BeheerAdminSite

urlpatterns = [
    path('',             site_root_view),
    path('account/',     include('Account.urls')),
    path('beheer/',      admin.site.urls),
    path('functie/',     include('Functie.urls')),
    path('logboek/',     include('Logboek.urls')),
    path('overig/',      include('Overig.urls')),
    path('plein/',       include('Plein.urls')),
    path('dof/',         include('Producten.urls')),
    path('email/',       include('Mailer.urls')),
    path('code/<code>/', DownloadView.as_view(), name='download'),
]

if settings.DEBUG:          # pragma: no cover
    import debug_toolbar
    urlpatterns.insert(0, path('__debug__', include(debug_toolbar.urls)))


# end of file
