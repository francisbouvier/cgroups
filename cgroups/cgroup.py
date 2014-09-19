#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

import os
import getpass

from cgroups.common import BASE_CGROUPS, CgroupsException
from cgroups.user import create_user_cgroups

HIERARCHIES = [
    'cpu',
    'memory',
]
MEMORY_DEFAULT = -1
CPU_DEFAULT = 1024

SWAPPINESS_DEFAULT = 60


class Cgroup(object):

    def __init__(self, name, hierarchies='all', user='current'):
        self.name = name
        # Get user
        self.user = user
        if self.user == 'current':
            self.user = getpass.getuser()
        # Get hierarchies
        if hierarchies == 'all':
            hierachies = HIERARCHIES
        self.hierarchies = [h for h in hierachies if h in HIERARCHIES]
        # Get user cgroups
        self.user_cgroups = {}
        system_hierarchies = os.listdir(BASE_CGROUPS)
        for hierarchy in self.hierarchies:
            if hierarchy not in system_hierarchies:
                raise CgroupsException(
                    "Hierarchy %s is not mounted" % hierarchy)
            user_cgroup = os.path.join(BASE_CGROUPS, hierarchy, self.user)
            self.user_cgroups[hierarchy] = user_cgroup
        create_user_cgroups(self.user, script=False)
        # Create name cgroups
        self.cgroups = {}
        for hierarchy, user_cgroup in self.user_cgroups.items():
            cgroup = os.path.join(user_cgroup, self.name)
            if not os.path.exists(cgroup):
                os.mkdir(cgroup)
            self.cgroups[hierarchy] = cgroup

    def _get_cgroup_file(self, hierarchy, file_name):
        return os.path.join(self.cgroups[hierarchy], file_name)

    def _get_user_file(self, hierarchy, file_name):
        return os.path.join(self.user_cgroups[hierarchy], file_name)

    def delete(self):
        for hierarchy, cgroup in self.cgroups.items():
            # Put all pids of name cgroup in user cgroup
            tasks_file = self._get_cgroup_file(hierarchy, 'tasks')
            with open(tasks_file, 'r+') as f:
                tasks = f.read().split('\n')
            user_tasks_file =  self._get_user_file(hierarchy, 'tasks')
            with open(user_tasks_file, 'a+') as f:
                f.write('\n'.join(tasks))
            os.rmdir(cgroup)

    # PIDS

    def add(self, pid):
        try:
            os.kill(pid, 0)
        except OSError:
            raise CgroupsException('Pid %s does not exists' % pid)
        for hierarchy, cgroup in self.cgroups.items():
            tasks_file = self._get_cgroup_file(hierarchy, 'tasks')
            with open(tasks_file, 'r+') as f:
                cgroups_pids = f.read().split('\n')
            if not str(pid) in cgroups_pids:
                with open(tasks_file, 'a+') as f:
                    f.write('%s\n' % pid)

    def remove(self, pid):
        try:
            os.kill(pid, 0)
        except OSError:
            raise CgroupsException('Pid %s does not exists' % pid)
        for hierarchy, cgroup in self.cgroups.items():
            tasks_file = self._get_cgroup_file(hierarchy, 'tasks')
            with open(tasks_file, 'r+') as f:
                pids = f.read().split('\n')
                if str(pid) in pids:
                    user_tasks_file = self._get_user_file(hierarchy, 'tasks')
                    with open(user_tasks_file, 'a+') as f:
                        f.write('%s\n' % pid)

    @property
    def pids(self):
        hierarchy = self.hierarchies[0]
        tasks_file = self._get_cgroup_file(hierarchy, 'tasks')
        with open(tasks_file, 'r+') as f:
            pids = f.read().split('\n')[:-1]
        pids = [int(pid) for pid in pids]
        return pids

    # CPU

    def _format_cpu_value(self, limit=None):
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
                    value = int(round(CPU_DEFAULT * limit))
        return value

    def set_cpu_limit(self, limit=None):
        if 'cpu' in self.cgroups:
            value = self._format_cpu_value(limit)
            cpu_shares_file = self._get_cgroup_file('cpu', 'cpu.shares')
            with open(cpu_shares_file, 'w+') as f:
                f.write('%s\n' % value)
        else:
            raise CgroupsException(
                'CPU hierarchy not available in this cgroup')

    @property
    def cpu_limit(self):
        if 'cpu' in self.cgroups:
            cpu_shares_file = self._get_cgroup_file('cpu', 'cpu.shares')
            with open(cpu_shares_file, 'r+') as f:
                value = int(f.read().split('\n')[0])
                value = int(round((value / CPU_DEFAULT) * 100))
                return value
        else:
            return None

    # MEMORY

    def _format_memory_value(self, unit, limit=None):
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

    def set_memory_limit(self, limit=None, unit='megabytes'):
        if 'memory' in self.cgroups:
            value = self._format_memory_value(unit, limit)
            memory_limit_file = self._get_cgroup_file(
                'memory', 'memory.limit_in_bytes')
            with open(memory_limit_file, 'w+') as f:
                f.write('%s\n' % value)
        else:
            raise CgroupsException(
                'MEMORY hierarchy not available in this cgroup')

    @property
    def memory_limit(self):
        if 'memory' in self.cgroups:
            memory_limit_file = self._get_cgroup_file(
                'memory', 'memory.limit_in_bytes')
            with open(memory_limit_file, 'r+') as f:
                value = f.read().split('\n')[0]
                value = int(int(value) / 1024 / 1024)
                return value
        else:
            return None

    def set_memsw_limit(self,limit=None,unit='megabytes'):
        if 'memory' in self.cgroups:
            value = self._format_memory_value(unit,limit)
            swap_limit_file = self._get_cgroup_file(
                'memory', 'memory.memsw.limit_in_bytes')
            with open(swap_limit_file,'w+') as f:
                f.write('%s\n' % value)
        else:
            raise CgroupsException(
                'MEMORY hierarchy not available in this cgroup')

    @property
    def memsw_limit(self):
        if 'memory' in self.cgroups:
            swap_limit_file = self._get_cgroup_file(
                'memory', 'memory.memsw.limit_in_bytes')
            with open(swap_limit_file,'r+') as f:
                value = f.read().split('\n')[0]
                value = int(int(value)/ 1024 / 1024)
                return value
        else:
            return None

    def set_swappiness(self,swappiness=SWAPPINESS_DEFAULT):
        if 'memory' in self.cgroups:
            swappiness = int(swappiness)
            if swappiness<0 and swappiness>100:
                raise CgroupsException("swappiness value must be in range 1..100")
            value = swappiness
            swappiness_file = self._get_cgroup_file(
                'memory', 'memory.swappiness')
            with open(swappiness_file,'w+') as f:
                f.write('%s\n' % value)
        else:
            raise CgroupsException(
                'MEMORY hierarchy not available in this cgroup')

    @property
    def swappiness(self):
        if 'memory' in self.cgroups:
            swappiness_file = self._get_cgroup_file(
                'memory', 'memory.swappiness')
            with open(swappiness_file,'r+') as f:
                value = f.read().split('\n')[0]
                value = int(value)
                return value
        else:
            return None

    @property
    def is_under_oom(self):
        if 'memory' in self.cgroups:
            oom_control_file = self._get_cgroup_file(
                'memory', 'memory.oom_control')
            with open(oom_control_file,'r+') as f:
                oom_kill_disable,under_oom = map(int,f.read().split('\n'))
                oom_kill_disable = True if oom_kill_disable == 1 else False

                under_oom = True if under_oom == 1 else False

                return under_oom
        else:
            return None

    def set_omm_kill(self,allow=True):
        if 'memory' in self.cgroups:
            oom_control_file = self._get_cgroup_file(
                'memory', 'memory.oom_control')
            oom_kill_disable = 0 if allow else 1
            under_oom = 1 if self.is_under_oom else 0
            with open(oom_control_file,'w+') as f:
                f.write("oom_kill_disable %s\nunder_oom %s\n" % (oom_kill_disable,under_oom))
        else:
            raise CgroupsException(
                'MEMORY hierarchy not available in this cgroup')

    def allow_kill_under_oom(self):
        self.set_omm_kill(allow=True)

    def disallow_kill_under_oom(self):
        self.set_omm_kill(allow=False)

    # FREEZER

    @property
    def freeze_state(self):
        if 'freezer' in self.cgroups:
            freezer_state_file = self._get_cgroup_file(
                'freezer', 'freezer.state')
            with open(freezer_state_file,'r+') as f:
                state = f.read().split('\n')[0]
                return state
        else:
            return None

    def set_freezer_state(self,state):
        if state not in ('THAWED','FROZEN'):
            raise CgroupsException("there is two values of freezer.state paramener available - THAWED|FROZEN.")
        if 'freezer' in self.cgroups:
            freezer_state_file = self._get_cgroup_file(
                'freezer', 'freezer.state')
            with open(freezer_state_file,'w+') as f:
                f.write("%s\n" % state)
        else:
            raise CgroupsException(
                'FREEZER hierarchy not available in this cgroup')

    def freeze(self):
        self.set_freezer_state(state="FROZEN")

    def unfreeze(self):
        self.set_freezer_state(state="THAWED")
