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

find . -name "*.pyc" -exec rm -rf {} \;
rm -f report.zip && git archive --prefix=report/ -o report.zip HEAD
