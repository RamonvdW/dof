# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from . import view_producten  #, view_opdrachten, view_leveringen

app_name = 'Producten'

urlpatterns = [

    path('producten/',
         view_producten.ProductenView.as_view(),
         name='producten'),

    path('producten/nieuw/',
         view_producten.NieuwProductView.as_view(),
         name='nieuw-product'),

    path('producten/<product_pk>/wijzig/',
         view_producten.WijzigProductView.as_view(),
         name='wijzig-product'),

    #path('opdrachten/',
    #     view_opdrachten.OpdrachtenView.as_view(),
    #     name='opdrachten'),

    #path('leveringen/',
    #     view_leveringen.LeveringenView.as_view(),
    #     name='leveringen'),
]

# end of file
