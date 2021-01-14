#!/bin/bash

#  Copyright (c) 2019-2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# start the background process
echo "[INFO] Starting achtergrondtaak verwerk_opdrachten (runtime: 60 minutes)"
./manage.py verwerk_opdrachten 60 &
sleep 1

# start the webserver
echo "[INFO] Starting runserver"
python manage.py runserver --settings=dof.settings_dev

# kill the background process
echo "[INFO] Stopping achtergrond taak verwerk_opdrachten"
pkill -f verwerk_opdrachten

# end of file

