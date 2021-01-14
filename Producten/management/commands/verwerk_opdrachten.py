# -*- coding: utf-8 -*-

#  Copyright (c) 2020-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# werk de tussenstand bij voor deelcompetities die niet afgesloten zijn
# zodra er nieuwe ScoreHist records zijn

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils.encoding import force_text
from Mailer.models import Inbox
from Overig.background_sync import BackgroundSync
from Producten.models import Opdracht
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

        self._sync = BackgroundSync(settings.BACKGROUND_SYNC__VERWERK_OPDRACHTEN)
        self._count_ping = 0

    def add_arguments(self, parser):
        parser.add_argument('duration', type=int,
                            choices={1, 2, 5, 7, 10, 15, 20, 30, 45, 60},
                            help="Aantal minuten actief blijven")
        parser.add_argument('--quick', action='store_true')     # for testing

    @staticmethod
    def _verwerk_mail_body(body):
        # TODO: sanity-check dat dit van de webshop komt

        # in de body zit een vrij tekstveld waar we niet per ongeluk op willen matchen
        # daar achter staat niets nuttigs meer, dus kap daar op af
        pos = body.find('Eventuele opmerkingen')
        if pos > 0:
            body = body[:pos + 21]

        # de body bestaat uit regels met tekst met 'foute' newlines
        # opsplitsen en deze newlines dumpen
        lines = body.splitlines()

        for line in lines:
            print(line)

    def _verwerk_ontvangen_mails(self):
        print('_verwerk_ontvangen_mails')
        for obj in Inbox.objects.filter(is_verwerkt=False):
            print('verwerk inbox %s' % obj.pk)
            try:
                data = json.loads(obj.mail_text)
            except json.JSONDecodeError:
                my_logger.error('Inbox pk=%s heeft geen valide json body' % obj.pk)
                obj.is_verwerkt = True
                #obj.save()
            else:
                # haal de plain-text uit de mail en ignore de rest
                body = data['TextBody']

                print('body gevonden: lengte=%s' % len(body))

                self._verwerk_mail_body(body)

                obj.is_verwerkt = True
                #obj.save()
        # for

    def _monitor_nieuwe_mutaties(self):
        # monitor voor nieuwe ScoreHist
        prev_count = 0      # moet 0 zijn: beschermd tegen query op lege mutatie tabel
        now = datetime.datetime.now()
        while now < self.stop_at:                   # pragma: no branch
            # self.stdout.write('tick')
            new_count = Inbox.objects.count()
            if new_count != prev_count:
                prev_count = new_count
                self._verwerk_ontvangen_mails()
                now = datetime.datetime.now()

            # wacht 5 seconden voordat we opnieuw in de database kijken
            # het wachten kan onderbroken worden door een ping, als er een nieuwe mutatie toegevoegd is
            secs = (self.stop_at - now).total_seconds()
            if secs > 1:                                    # pragma: no branch
                timeout = min(5.0, secs)
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
