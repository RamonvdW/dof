# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # volgorde afdwingen
    dependencies = [
        ('Account', 'm0001_squashed'),
    ]

    # migratie functies
    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_BB',
        ),
        migrations.RemoveField(
            model_name='account',
            name='is_Observer',
        ),
        migrations.RemoveField(
            model_name='accountemail',
            name='optout_functie_koppeling',
        ),
        migrations.RemoveField(
            model_name='accountemail',
            name='optout_reactie_klacht',
        ),
        migrations.DeleteModel(
            name='HanterenPersoonsgegevens',
        ),
    ]

# end of file
