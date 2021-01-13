# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.views import View
from django.http import HttpResponse
from .models import Inbox
import logging
import json


MAX_POST_SIZE = 256 * 1024      # 256kByte

my_logger = logging.getLogger('DOF.Mailer')


class ReceiverWebhookView(View):
    """ View voor het ontvangen van een e-mail via een post.
        post: ontvangen data wordt in de database gezet.
    """

    @staticmethod
    def post(request, *args, **kwargs):
        """ deze functie handelt het http-post verzoek af
            als de gebruiker op de Verstuur knop drukt krijgt deze functie de ingevoerde data.
        """

        # sla het bericht meteen op in de database
        # TODO: voorkom dat de database overstroomd wordt met garbage?
        Inbox(mail_text=request.body[:MAX_POST_SIZE]).save()       # afkappen voor de veiligheid

        return HttpResponse('OK')

# end of file
