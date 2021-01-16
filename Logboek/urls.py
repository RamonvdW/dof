# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from . import views

app_name = 'Logboek'

urlpatterns = [
    path('',
         views.LogboekRestView.as_view(),
         name='alles'),

    path('rest/',
         views.LogboekRestView.as_view(),
         name='rest'),

    path('accounts/',
         views.LogboekAccountsView.as_view(),
         name='accounts'),

    path('uitrol/',
         views.LogboekUitrolView.as_view(),
         name='uitrol'),
]

# end of file
