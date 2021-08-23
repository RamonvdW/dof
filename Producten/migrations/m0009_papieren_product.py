# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # volgorde afdwingen
    dependencies = [
        ('Producten', 'm0008_opdracht_regels'),
    ]

    # migratie functies
    operations = [
        migrations.AddField(
            model_name='product',
            name='papieren_product',
            field=models.BooleanField(default=False),
        ),
    ]

# end of file
