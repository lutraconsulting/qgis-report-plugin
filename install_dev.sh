#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

case "$OSTYPE" in
    solaris*) ;;
    darwin*)  ln -s $DIR/report ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/report ;;
    linux*)   ln -s $DIR/report ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/report  ;;
    bsd*)     ;;
    msys*)    ;;
    *)        ;;
esac
