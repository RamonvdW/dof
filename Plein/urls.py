# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from . import views

app_name = 'Plein'

urlpatterns = [
    path('',
         views.PleinView.as_view(),
         name='plein'),

    path('niet-ondersteund/',
         views.NietOndersteundView.as_view(),
         name='niet-ondersteund'),
]

# end of file
