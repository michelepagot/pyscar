#!/usr/bin/python
# coding=utf-8
"""
Module that contains the command line app.
"""
#  Why does this file exist, and why not put this in __main__?
#
#  You might be tempted to import things from __main__ later, but that will cause
#  problems: the code will get executed twice:
#
#  - When you run `python -mpysds011` python will execute
#    ``__main__.py`` as a script. That means there won't be any
#    ``pysds011.__main__`` in ``sys.modules``.
#  - When you import __main__ it will get executed again (as a module) because
#    there's no ``pysds011.__main__`` in ``sys.modules``.
#
#  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration

from pyscar import download
import argparse
import logging

DESCRIPTION = "Script to download an artifact from Jenkins starting from build URL and artifact name"
VERSION = __version__


def main(cmd_args):
    parser   = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('-o','--out', help="Local file where to store remote artifact")
    parser.add_argument('-u', '--url', help="Remote artifact URL", required=True)
    parser.add_argument('-V','--verbose', dest="verbose_count",
                        action="count", default=0,
                        help="Increases log verbosity")

    parsed_args = parser.parse_args(cmd_args)

    logging.basicConfig()
    log = logging.getLogger("relhelp")
    if parsed_args.verbose_count > 2:
        log.setLevel(logging.getLevelName("DEBUG"))
    elif parsed_args.verbose_count > 1:
        log.setLevel(logging.getLevelName("INFO"))
    else:
        log.setLevel(logging.getLevelName("WARNING"))

    log.debug("Create and use App")