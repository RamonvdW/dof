# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.conf import settings
from django.shortcuts import render, reverse
from django.views.generic import ListView, View, TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from Mailer.models import mailer_email_is_valide
from Overig.helpers import get_safe_from_ip
from .models import Levering, get_path_to_product_bestand
import logging
import time


TEMPLATE_LEVERINGEN_LIJST = 'producten/leveringen.dtl'
TEMPLATE_LEVERING_NIET_GEVONDEN = 'producten/levering-niet-gevonden.dtl'
TEMPLATE_LEVERING_EMAIL_INVOEREN = 'producten/levering-email-invoeren.dtl'

my_logger = logging.getLogger('DOF.Levering')


class LeveringenView(ListView):

    template_name = TEMPLATE_LEVERINGEN_LIJST

    # TODO: pagination support
    # TODO: zoek/filter mogelijkheden

    def get_queryset(self):
        if self.request.user.is_staff:
            qset = (Levering
                    .objects
                    .select_related('opdracht', 'product')
                    .order_by('-aangemaakt_op'))[:200]
        else:
            qset = (Levering
                    .objects
                    .filter(eigenaar=self.request.user)
                    .select_related('opdracht', 'product')
                    .order_by('-aangemaakt_op'))[:200]

        return qset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            context['is_staff'] = True

        return context


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

        # presenteer een formulier waar de gebruiker zijn e-mailadres in moet voeren
        # wat overeen moet komen met levering.to_email
        context = dict()

        taal = None
        code = kwargs['code'][:32]      # afkappen voor veiligheid
        if len(code) == 32:
            try:
                levering = (Levering
                            .objects
                            .select_related('product')
                            .get(url_code=code))
                taal = levering.product.taal
            except Levering.DoesNotExist:
                pass

        context['email_tekst'] = 'Please enter your e-mail address'
        context['knop_tekst'] = 'Submit'

        if not taal:
            # kies een van de beschikbare talen
            # zodat een willekeurige code altijd dezelfde taal geeft
            # (er moet niet af te leiden zijn of de code goed is)
            som = sum([ord(letter) for letter in code])
            keuze = som % len(settings.EMAIL_TALEN)
            context['email_tekst'] = settings.EMAIL_TALEN[keuze][1]
            context['knop_tekst'] = settings.EMAIL_TALEN[keuze][2]
        else:
            for landcode, invoer_tekst, knop_tekst in settings.EMAIL_TALEN:
                if landcode == taal:
                    context['email_tekst'] = invoer_tekst
                    context['knop_tekst'] = knop_tekst
            # for

        context['url_download'] = reverse('download', kwargs={'code': code})

        return render(request, TEMPLATE_LEVERING_EMAIL_INVOEREN, context)

    def post(self, request, *args, **kwargs):
        """ deze functie wordt aangeroepen als een POST request ontvangen is """

        # begrens hoe snel deze functie misbruikt kan worden
        time.sleep(1)

        code = kwargs['code'][:32]  # afkappen voor veiligheid

        email = request.POST.get('email', '')
        email = email.strip().lower()

        if len(code) != 32 or not mailer_email_is_valide(email):
            # geen goede code of geen valide email ingevoerd
            return self.get(request, *args, **kwargs)

        try:
            levering = (Levering
                        .objects
                        .get(url_code=code))
        except Levering.DoesNotExist:
            return render(request, TEMPLATE_LEVERING_NIET_GEVONDEN)

        if levering.is_geblokkeerd:
            return render(request, TEMPLATE_LEVERING_NIET_GEVONDEN)

        if levering.to_email.strip().lower() != email:
            # verkeerde e-mail: laat de gebruiker opnieuw een e-mail invoeren
            return self.get(request, *args, **kwargs)

        # zoek het bestand erbij en stuur deze over
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
            # bestand niet gevonden
            my_logger.error('Download levering %s (%s) mislukt: %s' % (levering.pk, fpath, str(exc)))
            return render(request, TEMPLATE_LEVERING_NIET_GEVONDEN)

        from_ip = get_safe_from_ip(request)
        my_logger.info('Download levering %s (%s) vanaf IP %s' % (levering.pk, fpath, from_ip))

        if levering.download_count > 0:
            levering.download_count -= 1
        if levering.download_count <= 0:
            levering.is_geblokkeerd = True
        levering.save()

        return response

# end of file
