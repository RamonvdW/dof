# -*- coding: utf-8 -*-

#  Copyright (c) 2020-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# werk de tussenstand bij voor deelcompetities die niet afgesloten zijn
# zodra er nieuwe ScoreHist records zijn

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F
from Account.models import Account
from Mailer.models import Inbox
from Overig.background_sync import BackgroundSync
from Producten.models import Product, Opdracht, BerichtTemplate
import django.db.utils
import datetime
import logging
import json


my_logger = logging.getLogger('DOF.Opdrachten')


class Command(BaseCommand):
    help = "Verwerk opdrachten (achtergrondtaak)"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.stop_at = datetime.datetime.now()
        self._verbose = False
        self._sync = BackgroundSync(settings.BACKGROUND_SYNC__VERWERK_OPDRACHTEN)
        self._count_ping = 0

    def add_arguments(self, parser):
        parser.add_argument('duration', type=int,
                            choices={1, 2, 5, 7, 10, 15, 20, 30, 45, 60},
                            help="Aantal minuten actief blijven")
        parser.add_argument('--quick', action='store_true')     # for testing

    def _maak_opdracht(self, inbox, items, lines):
        # TODO: sanity-check dat dit van de webshop komt

        try:
            email = items['E-mail']
            naam = items['Naam']
        except KeyError:
            if self._verbose:
                self.stderr.write('[ERROR] Inbox pk=%s heeft niet alle benodigde items' % inbox.pk)
                self.stderr.write('Dit zijn de items:')
                for key, value in items.items():
                    self.stderr.write('   %s / %s' % (key, value))
            my_logger.error('Inbox pk=%s heeft niet alle benodigde items' % inbox.pk)
            return False        # faal

        try:
            opdracht = Opdracht.objects.get(bron=inbox)
        except Opdracht.DoesNotExist:
            # maak een nieuwe opdracht aan
            opdracht = Opdracht()
            opdracht.bron = inbox
        else:
            # hergebruik de opdracht (voorkom duplicates)
            opdracht.producten.clear()

        opdracht.eigenaar = Account.objects.get(username=settings.DEFAULT_EIGENAAR)
        opdracht.to_email = email
        opdracht.to_naam = naam
        opdracht.save()

        taal = ''
        prod_links = ''
        # zoek matchende producten
        for prod in Product.objects.filter(eigenaar=opdracht.eigenaar):
            if prod.is_match(lines):
                opdracht.producten.add(prod)
                taal = prod.taal

                # TODO: download url genereren naar Levering
                url = settings.SITE_URL + '/download/tbd'
                prod_links += '%s: %s\n' % (prod.korte_beschrijving, url)

                if prod.handmatig_vrijgeven:
                    opdracht.is_vrijgegeven_voor_levering = False
        # for

        if prod_links == '':
            # geen producten kunnen matchen
            opdracht.is_vrijgegeven_voor_levering = False
            my_logger.error('Opdracht pk=%s niet kunnen koppelen aan een product' % opdracht.pk)
            opdracht.save()
            return False        # faal

        try:
            template = (BerichtTemplate
                        .objects
                        .get(eigenaar=opdracht.eigenaar,
                             taal=taal))
        except BerichtTemplate.DoesNotExist:
            # geen template kunnen maken
            opdracht.is_vrijgegeven_voor_levering = False
            my_logger.error('Geen template voor taal %s en eigenaar %s' % (
                                    repr(taal),
                                    opdracht.eigenaar.get_first_name()))
            opdracht.save()
            return False

        msg = template.intro
        msg = msg.replace('%NAME%', opdracht.to_naam)
        msg = msg.replace('%LINKS%', prod_links)

        opdracht.mail_body = msg
        opdracht.save()

        if opdracht.is_vrijgegeven_voor_levering:
            # TODO: ping taak voor verwerken van de opdracht (indien niet handmatig)
            pass

        # success
        return True

    def _verwerk_mail_body(self, inbox, body):
        # in de body zit een vrij tekstveld waar we niet per ongeluk op willen matchen
        # daar achter staat niets nuttigs meer, dus kap daar op af
        pos = body.find('Eventuele opmerkingen')
        if pos > 0:
            body = body[:pos + 21]

        pos = body.find('een nieuwe bestelling met ordernummer')
        if pos < 0:
            my_logger.info('Inbox pk=%s is geen bestelling' % inbox.pk)
            return True     # niet meer naar kijken

        # remove garbage
        body = body.replace('\xa0', '')
        for field in ('Naam', 'E-mail', 'Telefoon', 'Straat', 'Postcode', 'Plaats', 'Land'):
            body = body.replace(' %s: ' % field, '\n%s:\n' % field)
            body = body.replace(' %s:' % field, '\n%s:' % field)
        # for

        # de body bestaat uit regels met tekst met 'foute' newlines
        # opsplitsen en deze newlines dumpen
        lines = body.splitlines()

        # delete empty lines
        lines = [line for line in lines if len(line) > 0]

        # in de body vinden we key-value pairs op aparte regels
        # de keys eindigen op een dubbele punt
        items = dict()
        line_nr = 0
        while line_nr < len(lines):
            line = lines[line_nr]
            if line[-1] == ':' and line_nr+1 < len(lines):
                key = line[:-1]     # verwijder de dubbele punt
                value = lines[line_nr + 1]
                line_nr += 2

                if key in items:
                    my_logger.error('Inbox pk=%s geeft onverwacht een dupe item' % (inbox.pk, repr(key)))
                else:
                    items[key] = value
            else:
                line_nr += 1
        # while

        return self._maak_opdracht(inbox, items, lines)

    def _verwerk_ontvangen_mails(self):
        for obj in Inbox.objects.filter(is_verwerkt=False):
            try:
                data = json.loads(obj.mail_text)
            except json.JSONDecodeError:
                my_logger.error('Inbox pk=%s heeft geen valide json body' % obj.pk)
                obj.is_verwerkt = True
                obj.save()
            else:
                # haal de plain-text uit de mail en ignore de rest
                body = data['TextBody']
                if self._verwerk_mail_body(obj, body):
                    obj.is_verwerkt = True
                    obj.save()
        # for

    def _monitor_nieuwe_mutaties(self):
        # monitor voor nieuwe ScoreHist
        prev_count = 0      # moet 0 zijn: beschermd tegen query op lege mutatie tabel
        now = datetime.datetime.now()
        while now < self.stop_at:                   # pragma: no branch
            # self.stdout.write('tick')
            self._verwerk_ontvangen_mails()

            # wacht 30 seconden voordat we opnieuw in de database kijken
            # het wachten kan onderbroken worden door een ping,
            # als er een nieuwe mail ontvangen is of opnieuw analyseren gevraagd is
            secs = (self.stop_at - now).total_seconds()
            if secs > 1:                                    # pragma: no branch
                timeout = min(30.0, secs)
                if self._sync.wait_for_ping(timeout):       # pragma: no branch
                    self._count_ping += 1                   # pragma: no cover
            else:
                # near the end
                break       # from the while

            now = datetime.datetime.now()
        # while

    def _set_stop_time(self, **options):
        # bepaal wanneer we moeten stoppen (zoals gevraagd)
        # trek er nog eens 15 seconden vanaf, om overlap van twee cron jobs te voorkomen
        duration = options['duration']

        self.stop_at = (datetime.datetime.now()
                        + datetime.timedelta(minutes=duration)
                        - datetime.timedelta(seconds=15))

        # test moet snel stoppen dus interpreteer duration in seconden
        if options['quick']:        # pragma: no branch
            self.stop_at = (datetime.datetime.now()
                            + datetime.timedelta(seconds=duration))

        self.stdout.write('[INFO] Taak loopt tot %s' % str(self.stop_at))

    def handle(self, *args, **options):

        verbosity = int(options['verbosity'])
        if verbosity > 0:
            self._verbose = True

        self._set_stop_time(**options)

        # vang generieke fouten af
        try:
            self._monitor_nieuwe_mutaties()
        except django.db.utils.DataError as exc:        # pragma: no coverage
            self.stderr.write('[ERROR] Onverwachte database fout: %s' % str(exc))
        except KeyboardInterrupt:                       # pragma: no coverage
            pass

        self.stdout.write('[DEBUG] Aantal pings ontvangen: %s' % self._count_ping)

        self.stdout.write('Klaar')


"""
    performance debug helper:

    from django.db import connection

        q_begin = len(connection.queries)

        # queries here

        print('queries: %s' % (len(connection.queries) - q_begin))
        for obj in connection.queries[q_begin:]:
            print('%10s %s' % (obj['time'], obj['sql'][:200]))
        # for
        sys.exit(1)

    test uitvoeren met --debug-mode anders wordt er niets bijgehouden
"""

# end of file
