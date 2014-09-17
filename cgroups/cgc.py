#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import getpass
import logging
import argparse

import subprocess

from cgroups.common import BASE_CGROUPS, CgroupsException
from cgroups.user import get_user_info
from cgroups.user import create_user_cgroups

from cgroups import Cgroup

logger = logging.getLogger(__name__)

def run_command_with_cgroups_options(command,cpu=None,mem=None,swapless=False,cgroup=None):
    if cgroup is None:
        cg_name = ''
        if swapless:
            cg_name += 'swapless'
        cg_name += '_cpu'+str(cpu)
        if mem != -1:
            cg_name += '_mem'+str(mem)
        # print (cg_name)

    else:
        cg_name = cgroup

    cg = Cgroup(cg_name)

    if cpu is not None:
        cg.set_cpu_limit(cpu)

    if mem is not None:
        cg.set_memory_limit(mem)

    if swapless:
        cg.set_swappiness(0)

    def preexec_fn ():
        pid = os.getpid()
        print ("starting {} with pid {}".format(command,pid))
        cg.add(pid)

    process = subprocess.Popen([command],preexec_fn=preexec_fn)
    process.wait()

def main():
    parser = argparse.ArgumentParser(
            prog="cgc",
            description="cli tool for managing processes using Control Groups Linux mechanism"
        )

    parser.add_argument(
            '-v',
            '--verbose',
            dest='verbose',
            action='store',
            help='verbose actions level (DEBUG,INFO,WARN), default=INFO',
            default="INFO",
        )

    parser.add_argument(
            'action',
            choices=('useradd','run','cgadd','addpid','rmpid','cgls','frz','ufrz'),
            help="action to do",
        )

    parser.add_argument(
            '--command',
            dest='command',
            action='store',
            type=str,
            help='command to run with some cgroup configuration',
            default=None,
        )
    parser.add_argument(
            '--no-swap',
            dest='no_swap',
            action='store_true',
            help='run command with swap memmory limit set to 0 bytes'
        )
    parser.add_argument(
            '--cpu',
            dest='cpu',
            action='store',
            type=int,
            help='run command with some percent of cpu-resource',
            default=None,
        )
    parser.add_argument(
            '--mem',
            dest='mem',
            action='store',
            type=int,
            help='run command with memory limit',
            default=None
        )
    parser.add_argument(
            '--cgroup',
            dest='cgroup',
            action='store',
            type=str,
            help='cgroup name',
            default=None,
        )

    parser.add_argument(
            '--user',
            dest='user',
            action='store',
            help='username to grant privileges to use cgroups',
            default=None,
        )

    args = parser.parse_args()

    print (args)

    # Logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logstream = logging.StreamHandler()
    logstream.setFormatter(formatter)
    logger.addHandler(logstream)
    if args.verbose == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif args.verbose == 'INFO':
        logger.setLevel(logging.INFO)
    elif args.verbose == 'WARN':
        logger.setLevel(logging.WARN)
    else:
        logger.setLevel(logging.ERROR)
    logger.debug('Logging level: %s' % args.verbose)

    print (args)

    if args.action == "run":
        print ("runing command {}".format(args.command))
        run_command_with_cgroups_options(args.command,cpu=args.cpu,mem=args.mem,swapless=args.no_swap if args.no_swap else False,cgroup=args.cgroup)

    elif args.action == "useradd":
        print ("adding user {}".format(args.user))
        create_user_cgroups(args.user)

if __name__ == "__main__":
    main()
