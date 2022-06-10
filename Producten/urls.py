# -*- coding: utf-8 -*-

#  Copyright (c) 2021-2022 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from . import view_producten, view_opdrachten, view_leveringen  #, view_templates

app_name = 'Producten'

urlpatterns = [

    #path('templates',
    #     view_templates.TemplatesView.as_view(),
    #     name='templates'),

    path('producten/',
         view_producten.ProductenView.as_view(),
         name='producten'),

    path('producten/nieuw/',
         view_producten.NieuwProductView.as_view(),
         name='nieuw-product'),

    path('producten/<product_pk>/wijzig/',
         view_producten.WijzigProductView.as_view(),
         name='wijzig-product'),

    path('producten/<product_pk>/upload/',
         view_producten.UploadView.as_view(),
         name='upload-bestand'),

    path('opdrachten/',
         view_opdrachten.OpdrachtenView.as_view(),
         name='opdrachten'),

    path('opdrachten/<opdracht_pk>/bekijk/',
         view_opdrachten.OpdrachtDetailsView.as_view(),
         name='bekijk-opdracht'),

    path('opdrachten/<opdracht_pk>/opnieuw-analyseren/',
         view_opdrachten.OpdrachtOpnieuwAnalyserenView.as_view(),
         name='opnieuw-analyseren'),

    path('opdrachten/<opdracht_pk>/vrijgeven/',
         view_opdrachten.OpdrachtVrijgevenView.as_view(),
         name='opdracht-vrijgeven'),

    path('leveringen/',
         view_leveringen.LeveringenView.as_view(),
         name='leveringen'),

    path('leveringen/niet-gevonden/',
         view_leveringen.LeveringNietGevondenView.as_view(),
         name='levering-niet-gevonden'),

    path('leveringen/gratis/',
         view_leveringen.KlantgegevensGratisLeveringen.as_view(),
         name='gratis-leveringen'),

    path('leveringen/gratis/<product_naam>/',
         view_leveringen.KlantgegevensGratisLeveringen.as_view(),
         name='gratis-leveringen-product')
]

# end of file
