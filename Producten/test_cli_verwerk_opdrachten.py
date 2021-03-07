# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.test import TestCase, override_settings
from django.conf import settings
from django.core import management
from Mailer.models import Inbox
from Overig.e2ehelpers import E2EHelpers
from Producten.models import Product, Opdracht, Levering, get_path_to_product_bestand
import shutil
import io
import os


@override_settings(DOF_FILE_STORE='/tmp/test_dof/')
class TestProductenCliVerwerkOpdrachten(E2EHelpers, TestCase):
    """ unittests voor de Producten applicatie, management command verwerk_opdrachten """

    def _maak_producten_aan(self):
        producten = (
            # Erna
            ('PDF Rok Erna',           'NL', 'PDF Rok Erna', 'PDF Rock Erna', 'PDF skirt Erna'),
            ('PDF Rock Erna',          'DU', 'PDF Rok Erna', 'PDF Rock Erna', 'PDF skirt Erna'),
            ('PDF Skirt Erna',         'EN', 'PDF Rok Erna', 'PDF Rock Erna', 'PDF skirt Erna'),

            # Francis
            ('PDF Tricot top Francis', 'NL', 'PDF Tricot top Francis', 'PDF Shirt Francis', 'PDF Jersey tee Francis'),
            ('PDF Shirt Francis',      'DU', 'PDF Tricot top Francis', 'PDF Shirt Francis', 'PDF Jersey tee Francis'),
            ('PDF Jersey tee Francis', 'EN', 'PDF Tricot top Francis', 'PDF Shirt Francis', 'PDF Jersey tee Francis'),

            # Zak
            ('PDF zijnaad zak',        'NL', 'PDF zijnaad zak', 'PDF Seitennaht Tasche', 'PDF sideseam pocket'),
            ('PDF Seitennaht Tasche',  'DU', 'PDF zijnaad zak', 'PDF Seitennaht Tasche', 'PDF sideseam pocket'),
            ('PDF sideseam pocket',    'EN', 'PDF zijnaad zak', 'PDF Seitennaht Tasche', 'PDF sideseam pocket')
        )

        for kort, taal, match1, match2, match3 in producten:
            prod = Product(eigenaar=self._eigenaar,
                           korte_beschrijving=kort,
                           taal=taal,
                           naam_bestand='dummy.pdf',
                           handmatig_vrijgeven=True,
                           match_1=match1,
                           match_2=match2,
                           match_3=match3)
            prod.save()

            fpath, _ = get_path_to_product_bestand(prod)
            os.makedirs(os.path.dirname(fpath))
            with open(fpath, 'w') as f:
                f.write('dummy')
        # for

    def setUp(self):
        """ initialisatie van de test case """

        shutil.rmtree(settings.DOF_FILE_STORE)

        self._eigenaar = self.e2e_create_account(settings.DEFAULT_EIGENAAR, 'eigenaar@test.nl', 'Eigenaar')

        self._maak_producten_aan()

        self._test_mails = 'Producten/management/testfiles/mail_%02d.txt'   # mail_nr

    def _prep_input(self, mail_nr):
        with open(self._test_mails % mail_nr, 'r') as f:
            mail = f.read()
        Inbox(mail_text=mail).save()

    @staticmethod
    def _verwerk():
        err = io.StringIO()
        out = io.StringIO()
        management.call_command('verwerk_opdrachten', 2, '--quick', stderr=err, stdout=out)
        return err.getvalue(), out.getvalue()

    def _test_opdracht(self, nr, chk_template_taal, chk_prods, debug=False):

        chk_aantal = len(chk_prods)
        gekozen = 'Gekozen taal voor de levering: %s' % chk_template_taal

        self._prep_input(nr)
        out, err = self._verwerk()
        self.assertFalse('[ERROR]' in err)

        self.assertEqual(1, Opdracht.objects.count())
        opdracht = Opdracht.objects.all()[0]

        if debug:
            print('opdracht.regels:', opdracht.regels)
        self.assertTrue(gekozen in opdracht.regels)
        self.assertEqual(chk_aantal, opdracht.regels.count('1 x'))

        self.assertEqual(chk_aantal, opdracht.producten.count())
        to_be_found = list(chk_prods)
        for prod in opdracht.producten.all():
            tup = (prod.taal, prod.korte_beschrijving)
            if tup not in chk_prods:
                self.fail(msg='Verkeerd product gekozen: %s' % repr(tup))
            to_be_found.remove(tup)
        # for

        if len(to_be_found) > 0:
            msg = 'Niet gevonden producten (%s):\n' % len(to_be_found)
            for tup in to_be_found:
                msg += '    %s' % repr(tup)
            self.fail(msg=msg)

        self.assertFalse(opdracht.is_vrijgegeven_voor_levering)
        self.assertFalse(opdracht.is_afgehandeld)

        self.assertEqual(chk_aantal, Levering.objects.count())

    def test_01(self):
        self._test_opdracht(1, 'NL', (('NL', 'PDF Rok Erna'),))

    def test_02(self):
        self._test_opdracht(2, 'DU', (('DU', 'PDF Rock Erna'),))

    def test_03(self):
        self._test_opdracht(3, 'DU', (('NL', 'PDF Rok Erna'),))

    def test_04(self):
        self._test_opdracht(4, 'NL', (('NL', 'PDF Rok Erna'),
                                      ('EN', 'PDF Skirt Erna')))

    def test_05(self):
        self._test_opdracht(5, 'NL', (('NL', 'PDF Tricot top Francis'),))

    def test_06(self):
        self._test_opdracht(6, 'EN', (('EN', 'PDF Jersey tee Francis'),))

    def test_07(self):
        self._test_opdracht(7, 'EN', (('DU', 'PDF Shirt Francis'),))

    def test_08(self):
        self._test_opdracht(8, 'NL', (('NL', 'PDF Rok Erna'),
                                      ('NL', 'PDF zijnaad zak'),))

# end of file
