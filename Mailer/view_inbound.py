# -*- coding: utf-8 -*-

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.views import View
from django.http import HttpResponse
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
        my_logger.info('ReceiverWebhook: request.body=%s' % repr(request.body))

        try:
            data = json.loads(request.body[:MAX_POST_SIZE])        # afkappen voor veiligheid
        except json.JSONDecodeError:
            my_logger.warn('json decode error')
            pass
        else:
            my_logger.info('json data: %s' % json.dumps(data))

            try:
                print('From: %s' % data['From'])
                print('MessageStream: %s' % data['MessageStream'])
                print('FromName: %s' % data['FromName'])
                print('Date: %s' % data['Date'])
                print('Subject: %s' % data['Subject'])
                print('TextBody: %s' % data['TextBody'])
                print('HtmlBody: %s' % data['HtmlBody'])
            except KeyError:
                pass

        return HttpResponse('OK')

# end of file
