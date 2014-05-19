#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

import os

from cgroups.exceptions import CgroupsException
from cgroups.utils import get_user_cgroups

MEMORY_DEFAULT = -1
CPU_DEFAULT = 1024


def _get_cgroup_hierarchy(name, hierarchy):
    user_cgroup = get_user_cgroups()[hierarchy]
    cgroup = os.path.join(user_cgroup, name)
    if os.path.exists(cgroup):
        return cgroup
    else:
        raise CgroupsException('Cgroup %s does not exists' % name)


# CPU

def _get_cpu_value(limit=None):
    if limit is None:
        value = CPU_DEFAULT
    else:
        try:
            limit = float(limit)
        except ValueError:
            raise CgroupsException('Limit must be convertible to a float')
        else:
            if limit <= float(0) or limit > float(100):
                raise CgroupsException('Limit must be between 0 and 100')
            else:
                limit = limit / 100
                value = int(CPU_DEFAULT * limit)
    return value


def cpu_limit(name, limit=None):
    cgroup = _get_cgroup_hierarchy(name, 'cpu')
    value = _get_cpu_value(limit)
    cpu_shares_file = os.path.join(cgroup, 'cpu.shares')
    with open(cpu_shares_file, 'w+') as f:
        f.write('%s\n' % value)


# MEMORY

def _get_memory_value(unit, limit=None):
    units = ('bytes', 'kilobytes', 'megabytes', 'gigabytes')
    if unit not in units:
        raise CgroupsException('Unit must be in %s' % units)
    if limit is None:
        value = MEMORY_DEFAULT
    else:
        try:
            limit = int(limit)
        except ValueError:
            raise CgroupsException('Limit must be convertible to an int')
        else:
            if unit == 'bytes':
                value = limit
            elif unit == 'kilobytes':
                value = limit * 1024
            elif unit == 'megabytes':
                value = limit * 1024 * 1024
            elif unit == 'gigabytes':
                value = limit * 1024 * 1024 * 1024
    return value


def memory_limit(name, limit=None, unit='megabytes'):
    cgroup = _get_cgroup_hierarchy(name, 'memory')
    value = _get_memory_value(unit, limit)
    memory_limit_file = os.path.join(cgroup, 'memory.limit_in_bytes')
    with open(memory_limit_file, 'w+') as f:
        f.write('%s\n' % value)
