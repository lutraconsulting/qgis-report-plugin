#!/bin/bash
###########################################################################
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
###########################################################################

set -e

##### PYTHON

PYFILES=$(find . -maxdepth 1 -type f -name "*.py" )
for i in $PYFILES; do
    echo "$i"
    autopep8 --in-place --ignore=E261,E265,E402,E501 "$i"
done
