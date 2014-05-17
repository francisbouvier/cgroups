#! /usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import shutil

from pycgroups.utils import get_user_cgroups


def create(name):
    for user_cgroup in get_user_cgroups().values():
        cgroup = os.path.join(user_cgroup, name)
        if not os.path.exists(cgroup):
            os.mkdir(cgroup)


def delete(name):
    for user_cgroup in get_user_cgroups().values():
        cgroup = os.path.join(user_cgroup, name)
        if os.path.exists(cgroup):
            os.rmdir(cgroup)
