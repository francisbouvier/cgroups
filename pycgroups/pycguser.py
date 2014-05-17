#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import logging
import argparse


def main():

    # Logging
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logstream = logging.StreamHandler()
    logstream.setFormatter(formatter)
    logger.addHandler(logstream)
    logger.setLevel(logging.DEBUG)

    # Arguments
    parser = argparse.ArgumentParser(
        description='Allow a non-root user to use cgroups')
    parser.add_argument(
        '-u', '--user', required=False,
        help='User to grant privileges to use cgroups'
    )

    args = parser.parse_args()
    logger.debug(args.user)


if __name__ == '__main__':
    main()
