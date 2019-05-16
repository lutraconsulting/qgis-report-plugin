#-----------------------------------------------------------
# Copyright (C) 2016 Peter Petrik for Lutra Consulting
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qgis.core import *
from qgis.utils import *


def get_file_path(*paths):
    temp_dir = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(temp_dir, *paths)
    return path


def get_ui_file(name):
    return get_file_path('ui', name)


def add_deps(name):
    import sys
    dep = get_file_path('deps', name)
    sys.path.append(dep)


def colored_icon(color):
    pixmap = QPixmap(15, 15)
    pixmap.fill(QColor("#" + str(color)))
    icon = QIcon(pixmap)
    return icon


def label_img(widget, name):
    img = get_file_path('images', name)
    pixmap = QPixmap(img)
    widget.setPixmap(pixmap)
    widget.setMask(pixmap.mask())
    widget.show()


def save_settings(key, val):
    settings = QSettings()
    settings.beginGroup("/qgis-report-plugin")
    settings.setValue(key, val)


def load_settings(key):
    settings = QSettings()
    settings.beginGroup("/qgis-report-plugin")
    return settings.value(key, "", type=str)
