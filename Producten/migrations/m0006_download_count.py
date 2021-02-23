# -*- coding: utf-8 -*-

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import migrations, models


class Migration(migrations.Migration):

    """ Migratie class voor dit deel van de applicatie """

    # dit is de eerste
    dependencies = [
        ('Producten', 'm0005_levering_update'),
    ]

    # migratie functies
    operations = [
        migrations.AddField(
            model_name='levering',
            name='download_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='berichttemplate',
            name='taal',
            field=models.CharField(choices=[('NL', 'Nederlands'), ('EN', 'Engels'), ('DU', 'Duits'), ('FR', 'Frans'), ('SE', 'Zweeds'), ('TR', 'Turks')], max_length=2),
        ),
        migrations.AlterField(
            model_name='product',
            name='taal',
            field=models.CharField(choices=[('NL', 'Nederlands'), ('EN', 'Engels'), ('DU', 'Duits'), ('FR', 'Frans'), ('SE', 'Zweeds'), ('TR', 'Turks')], default='NL', max_length=2),
        ),
    ]

# end of file
