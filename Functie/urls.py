# -*- coding: utf-8 -*-

#  Copyright (c) 2020-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from . import view_otp

app_name = 'Functie'

urlpatterns = [

    path('otp-controle/',
         view_otp.OTPControleView.as_view(),
         name="otp-controle"),

    path('otp-koppelen/',
         view_otp.OTPKoppelenView.as_view(),
         name="otp-koppelen"),
]

# end of file
