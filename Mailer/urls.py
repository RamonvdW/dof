# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import view_inbound

app_name = 'Mailer'

urlpatterns = [
    path('inbound/',
         csrf_exempt(view_inbound.ReceiverWebhookView.as_view()),
         name='receiver-webhook'),
]

# end of file
