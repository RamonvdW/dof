# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView, View, TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from Overig.helpers import get_safe_from_ip
from .models import Levering, get_path_to_product_bestand
import logging
import os


TEMPLATE_LEVERING_NIET_GEVONDEN = 'producten/levering-niet-gevonden.dtl'

my_logger = logging.getLogger('DOF.Levering')


class LeveringenView(ListView):
    pass


class LeveringNietGevondenView(TemplateView):

    """ deze view toont een foutmelding als de download code niet werkt """

    template_name = 'producten/levering-niet-gevonden.dtl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DownloadView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        """ deze functie wordt aangeroepen als een GET request ontvangen is """

        code = kwargs['code'][:32]      # afkappen voor veiligheid
        if len(code) != 32:
            return render(request, TEMPLATE_LEVERING_NIET_GEVONDEN)

        try:
            levering = Levering.objects.get(url_code=code)
        except Levering.DoesNotExist:
            return render(request, TEMPLATE_LEVERING_NIET_GEVONDEN)

        # TODO: overweeg de gebruiker zijn e-mailadres in te laten voeren (levering.to_email)

        product = levering.product
        fpath, naam = get_path_to_product_bestand(product)

        klein = naam.lower()
        if '.zip' in klein:
            content_type = 'application/zip'
        elif '.pdf' in klein:
            content_type = 'application/pdf'
        else:
            content_type = 'application/octet-stream'

        try:
            with open(fpath, 'rb') as file_handle:
                response = HttpResponse(file_handle, content_type=content_type)
                response['Content-Disposition'] = 'attachment; filename="%s"' % naam
        except (FileNotFoundError, OSError) as exc:
            my_logger.error('Download levering %s (%s) mislukt: %s' % (levering.pk, fpath, str(exc)))
            return render(request, TEMPLATE_LEVERING_NIET_GEVONDEN)

        from_ip = get_safe_from_ip(request)
        my_logger.info('Download levering %s (%s) vanaf IP %s' % (levering.pk, fpath, from_ip))

        return response

# end of file
