# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # dit is de eerste
    dependencies = [
        ('Producten', 'm0004_meer_funcs'),
    ]

    # migratie functies
    operations = [
        migrations.AddField(
            model_name='levering',
            name='is_geblokkeerd',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='levering',
            name='url_code',
            field=models.CharField(default='', max_length=32),
        ),
    ]

# end of file
