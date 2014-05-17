#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os

from pycgroups.utils import get_user_cgroups


def create(name):
    for user_cgroup in get_user_cgroups().values():
        cgroup = os.path.join(user_cgroup, name)
        if not os.path.exists(cgroup):
            os.mkdir(cgroup)


def delete(name):
    for hierarchy, user_cgroup in get_user_cgroups().items():
        cgroup = os.path.join(user_cgroup, name)
        if os.path.exists(cgroup):
            # Put pids in cgroup user root hierarchy
            tasks_file = os.path.join(cgroup, 'tasks')
            with open(tasks_file, 'r+') as f:
                tasks = f.read().split('\n')
            root_tasks_file = os.path.join(user_cgroup, 'tasks')
            with open(root_tasks_file, 'a+') as f:
                f.write('\n'.join(tasks))
            os.rmdir(cgroup)
