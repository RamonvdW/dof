#!/bin/bash

#  Copyright (c) 2021 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

# ga naar de directory waar het script staat
cd $(dirname $0)

rm requirements.txt
pip-compile requirements.in

rm requirements_dev.txt
pip-compile requirements_dev.in

# end of file

