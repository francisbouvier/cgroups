#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os

from pycgroups.exceptions import PyCgroupsException
from pycgroups.utils import get_user_cgroups


def add(name, pid):
    try:
        os.kill(pid, 0)
    except OSError:
        raise PyCgroupsException('Pid %s does not exists' % pid)
    for user_cgroup in get_user_cgroups().values():
        cgroup = os.path.join(user_cgroup, name)
        if os.path.exists(cgroup):
            tasks_file = os.path.join(cgroup, 'tasks')
            add = True
            if os.path.exists(tasks_file):
                with open(tasks_file, 'r+') as f:
                    cgroups_pids = f.read().split('\n')
                    if str(pid) in cgroups_pids:
                        add = False
                    else:
                        f = open(tasks_file, 'a+')
            else:
                f = open(tasks_file, 'w+')
            if add:
                f.write('%s\n' % pid)
                f.close()
        else:
            raise PyCgroupsException('Cgroup %s does not exists' % name)


def remove(name, pid):
    try:
        os.kill(pid, 0)
    except OSError:
        raise PyCgroupsException('Pid %s does not exists' % pid)
    for hierarchy, user_cgroup in get_user_cgroups().items():
        cgroup = os.path.join(user_cgroup, name)
        if os.path.exists(cgroup):
            tasks_file = os.path.join(cgroup, 'tasks')
            if os.path.exists(tasks_file):
                with open(tasks_file, 'r+') as f:
                    cgroups_pids = f.read().split('\n')
                    if str(pid) in cgroups_pids:
                        root_tasks_file = os.path.join(user_cgroup, 'tasks')
                        with open(root_tasks_file, 'a+') as f:
                            f.write('%s\n' % pid)
        else:
            raise PyCgroupsException('Cgroup %s does not exists' % name)
