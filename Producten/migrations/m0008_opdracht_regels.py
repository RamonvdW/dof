# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # volgorde afdwingen
    dependencies = [
        ('Producten', 'm0007_singular_plural'),
    ]

    # migratie functies
    operations = [
        migrations.AddField(
            model_name='opdracht',
            name='regels',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='opdracht',
            name='subject',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='berichttemplate',
            name='subject',
            field=models.CharField(default='', max_length=100),
        ),
    ]

# end of file
