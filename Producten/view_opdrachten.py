# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.conf import settings
from django.urls import Resolver404
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from Account.rechten import account_rechten_is_otp_verified
from Mailer.models import Inbox, mailer_queue_email
from Overig.background_sync import BackgroundSync
from .models import Opdracht
import json
import time


TEMPLATE_OPDRACHT_LIJST = 'producten/opdrachten.dtl'
TEMPLATE_OPDRACHT_DETAILS = 'producten/opdracht-details.dtl'

verwerk_ping = BackgroundSync(settings.BACKGROUND_SYNC__VERWERK_OPDRACHTEN)


class OpdrachtenView(UserPassesTestMixin, ListView):

    """ Django class-based view voor de activiteiten van de gebruikers """

    # class variables shared by all instances
    template_name = TEMPLATE_OPDRACHT_LIJST

    # TODO: pagination support
    # TODO: zoek/filter mogelijkheden

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Plein:plein'))

    def _make_link_urls(self, context):
        # voorbereidingen voor een regel met volgende/vorige links
        # en rechtstreekse links naar een 10 pagina's
        links = list()

        num_pages = context['paginator'].num_pages
        page_nr = context['page_obj'].number

        # previous
        if page_nr > 1:
            tup = ('vorige', self.base_url + '?page=%s' % (page_nr - 1))
            links.append(tup)
        else:
            tup = ('vorige_disable', '')
            links.append(tup)

        # block van 10 pagina's; huidige pagina in het midden
        range_start = page_nr - 5
        range_end = range_start + 9
        if range_start < 1:
            range_end += (1 - range_start)  # 1-0=1, 1--1=2, 1--2=3, etc.
            range_start = 1
        if range_end > num_pages:
            range_end = num_pages
        for pgnr in range(range_start, range_end+1):
            tup = ('%s' % pgnr, self.base_url + '?page=%s' % pgnr)
            links.append(tup)
        # for

        # next
        if page_nr < num_pages:
            tup = ('volgende', self.base_url + '?page=%s' % (page_nr + 1))
            links.append(tup)
        else:
            tup = ('volgende_disable', '')
            links.append(tup)

        return links

    def get_queryset(self):
        if self.request.user.is_staff:
            qset = (Opdracht
                    .objects
                    .order_by('-aangemaakt_op'))[:200]  # nieuwste bovenaan
        else:
            qset = (Opdracht
                    .objects
                    .filter(eigenaar=self.request.user)
                    .order_by('-aangemaakt_op'))[:200]        # nieuwste bovenaan

        for obj in qset:
            obj.url_bekijk = reverse('Producten:bekijk-opdracht',
                                     kwargs={'opdracht_pk': obj.pk})
        return qset

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        if context['is_paginated']:
            context['page_links'] = self._make_link_urls(context)
            context['active'] = str(context['page_obj'].number)

        if self.request.user.is_staff:
            context['is_staff'] = True

        return context


class OpdrachtDetailsView(UserPassesTestMixin, TemplateView):

    """ Django class-based view voor de activiteiten van de gebruikers """

    # class variables shared by all instances
    template_name = TEMPLATE_OPDRACHT_DETAILS

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Plein:plein'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            context['is_staff'] = True

        try:
            opdracht_pk = int(kwargs['opdracht_pk'][:6])    # afkappen voor veiligheid

            if self.request.user.is_staff:
                opdracht = (Opdracht
                            .objects
                            .select_related('bron')
                            .get(pk=opdracht_pk))
            else:
                opdracht = (Opdracht
                            .objects
                            .select_related('bron')
                            .get(pk=opdracht_pk,
                                 eigenaar=self.request.user))  # alleen eigen producten
        except (ValueError, Opdracht.DoesNotExist):
            raise Resolver404()

        context['opdracht'] = opdracht

        inbox = opdracht.bron
        try:
            data = json.loads(inbox.mail_text)
        except json.JSONDecodeError:
            context['inbox_error'] = 'Kan de mail niet tonen (fout 1)'
        else:
            # haal de plain-text uit de mail en ignore de rest
            try:
                body = data['TextBody']
            except KeyError:
                context['inbox_error'] = 'Kan de mail niet tonen (fout 2)'
            else:
                body = body.replace('\r\n\r\n', '\n')
                context['inbox_body'] = body.splitlines()

        if not opdracht.is_afgehandeld:
            if not opdracht.is_vrijgegeven_voor_levering:
                context['url_vrijgeven'] = reverse('Producten:opdracht-vrijgeven',
                                                   kwargs={'opdracht_pk': opdracht.pk})

                context['url_opnieuw_analyseren'] = reverse('Producten:opnieuw-analyseren',
                                                            kwargs={'opdracht_pk': opdracht.pk})

        context['url_terug'] = reverse('Producten:opdrachten')

        return context


class OpdrachtOpnieuwAnalyserenView(UserPassesTestMixin, View):

    """ Django class-based view voor het opnieuw analyseren van een opdracht """

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Plein:plein'))

    @staticmethod
    def post(request, *args, **kwargs):
        eigenaar = request.user

        try:
            opdracht_pk = int(kwargs['opdracht_pk'][:6])    # afkappen voor veiligheid
            if request.user.is_staff:
                opdracht = (Opdracht
                            .objects
                            .select_related('bron')
                            .get(pk=opdracht_pk))
            else:
                opdracht = (Opdracht
                            .objects
                            .select_related('bron')
                            .get(pk=opdracht_pk,
                                 eigenaar=eigenaar))            # alleen eigen producten
        except (ValueError, Opdracht.DoesNotExist):
            raise Resolver404()

        if opdracht.is_afgehandeld or opdracht.is_vrijgegeven_voor_levering:
            raise Resolver404()

        # zet de bron (e-mail) opnieuw op verwerken
        inbox = opdracht.bron
        inbox.is_verwerkt = False
        inbox.save()

        # start the achtergrond taak
        verwerk_ping.ping()

        # wacht maximaal 3 seconden tot de achtergrond klaar is
        interval = 0.2  # om steeds te verdubbelen
        total = 0.0  # om een limiet te stellen
        while not inbox.is_verwerkt and total + interval <= 3.0:
            time.sleep(interval)
            total += interval  # 0.0 --> 0.2, 0.6, 1.4, 3.0, 6.2
            interval *= 2      # 0.2 --> 0.4, 0.8, 1.6, 3.2
            inbox = Inbox.objects.get(pk=inbox.pk)
        # while

        # we hadden of een timeout, of het is gelukt
        try:
            opdracht = Opdracht.objects.get(bron=inbox)
        except Opdracht.DoesNotExist:
            # niet gevonden - dan maar terug naar de grote lijst
            url = reverse('Producten:opdrachten')
        else:
            # wel gevonden - meteen tonen
            url = reverse('Producten:bekijk-opdracht',
                          kwargs={'opdracht_pk': opdracht.pk})

        return HttpResponseRedirect(url)


class OpdrachtVrijgevenView(UserPassesTestMixin, View):

    """ Django class-based view voor het toevoegen van een product """

    def test_func(self):
        """ called by the UserPassesTestMixin to verify the user has permissions to use this view """
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        """ gebruiker heeft geen toegang --> redirect naar het plein """
        return HttpResponseRedirect(reverse('Plein:plein'))

    @staticmethod
    def post(request, *args, **kwargs):
        eigenaar = request.user

        try:
            opdracht_pk = int(kwargs['opdracht_pk'][:6])    # afkappen voor veiligheid
            opdracht = (Opdracht
                        .objects
                        .select_related('bron')
                        .get(pk=opdracht_pk,
                             eigenaar=eigenaar))            # alleen eigen producten
        except (ValueError, Opdracht.DoesNotExist):
            raise Resolver404()

        if opdracht.is_afgehandeld or opdracht.is_vrijgegeven_voor_levering:
            raise Resolver404()

        opdracht.is_vrijgegeven_voor_levering = True
        opdracht.save()

        mailer_queue_email(opdracht.to_email,
                           opdracht.subject,
                           opdracht.mail_body)

        opdracht.is_afgehandeld = True
        opdracht.save()

        url = reverse('Producten:bekijk-opdracht',
                      kwargs={'opdracht_pk': opdracht.pk})
        return HttpResponseRedirect(url)


# end of file
