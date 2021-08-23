# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # volgorde afdwingen
    dependencies = [
        ('Producten', 'm0006_download_count'),
    ]

    # migratie functies
    operations = [
        migrations.RenameField(
            model_name='berichttemplate',
            old_name='outro',
            new_name='plural',
        ),
        migrations.RenameField(
            model_name='berichttemplate',
            old_name='intro',
            new_name='singular',
        ),
        migrations.AlterField(
            model_name='product',
            name='handmatig_vrijgeven',
            field=models.BooleanField(default=True),
        ),
    ]

# end of file
