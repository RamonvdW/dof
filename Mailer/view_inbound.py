# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.conf import settings
from django.views import View
from django.http import HttpResponse
from Overig.background_sync import BackgroundSync
from .models import Inbox


MAX_POST_SIZE = 256 * 1024      # 256kByte

verwerk_ping = BackgroundSync(settings.BACKGROUND_SYNC__VERWERK_OPDRACHTEN)


class ReceiverWebhookView(View):
    """ View voor het ontvangen van een e-mail via een post.
        post: ontvangen data wordt in de database gezet.
    """

    @staticmethod
    def post(request, *args, **kwargs):
        """ deze functie handelt het http-post verzoek af
            als de gebruiker op de Verstuur knop drukt krijgt deze functie de ingevoerde data.
        """

        # TODO: voorkom dat de database overstroomd wordt met garbage!
        #       geheime code toevoegen als url parameter?
        #       maximum aantal niet-verwerkte mails (100?)

        # sla het bericht meteen op in de database

        # limiet van een body is 2.5MB (zie DATA_UPLOAD_MAX_MEMORY_SIZE)
        body = request.body.decode('utf-8')
        Inbox(mail_text=body[:MAX_POST_SIZE]).save()       # afkappen voor de veiligheid

        verwerk_ping.ping()

        return HttpResponse('OK')

# end of file
