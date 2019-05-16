#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -f report.zip && cd report && git archive --prefix=report/ -o ../report.zip HEAD