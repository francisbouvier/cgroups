# cgroups

*cgroups* is a library for managing Linux kernel cgroups.

`cgroups` is a great Linux kernel feature used to control process ressources by groups.

For now the library can only handle `cpu` and `memory` cgroups.


## Quick start

Let's say you have some workers and you want them to use no more than 50 % of the CPU and no more than 500 Mb of memory.

```python
import os
import subprocess

from cgroups import Cgroup

# First we create the cgroup 'charlie' and we set it's cpu and memory limits
cg = Cgroup('charlie')
cg.set_cpu_limit(50)
cg.set_memory_limit(500)

# Then we a create a function to add a process in the cgroup
def in_my_cgroup():
	pid  = os.getpid()
	cg = Cgroup('charlie')
	cg.add(pid)

# And we pass this function to the preexec_fn parameter of the subprocess call
# in order to add the process to the cgroup
p1 = subprocess.Popen(['worker_1'], preexec_fn=in_my_cgroup)
p2 = subprocess.Popen(['worker_2'], preexec_fn=in_my_cgroup)
p3 = subprocess.Popen(['worker_3'], preexec_fn=in_my_cgroup)

# Processes worker_1, worker_2, and worker_3 are now in the cgroup 'charlie'
# and all limits of this cgroup apply to them

# We can change the cgroup limit while those process are still running
cg.set_cpu_limit(80)

# And of course we can add other applications to the cgroup
# Let's say we have an application running with pid 27033
cg.add(27033)
```

*Note*: You have to execute this add with root privilages or with sudo (see below **Root and non-root usage**).


## Installation

```bash
pip install cgroups
```


## Requirements

**Linux and cgroups**

The `cgroups` feature is only available on Linux systems with a recent kernel and with the cgroups filesystem mounted at `/sys/fs/cgroup` (which is the case of most Linux distributions since 2012).

If the cgroups filesystem is mounted elsewhere you can change the `BASE_CGROUPS` value to accomidate:

```python
from cgroups import BASE_CGROUPS

BASE_CGROUPS = 'path_to_cgroups_filesystem'
```

**Root and non-root usage**

To use *cgroups* the current user has to have root privileges **OR** existing cgroups sub-directories.

In order to create those cgroups sub-directories you use the `user_cgroups` command as root.

```bash
sudo user_cgroups USER
```

*N.B.*: This will only give the user permissions to manage cgroups in his or her own sub-directories and process. It wiil not give the user permissions on other cgroups, process, or system commands.

*N.B.*: You only need to execute this script once.


## Usage

**class Cgroup(name, hierarchies='all', user='current')**

Create or load a cgroup.

*name* is the name of the cgroup.

*hierarchies* is a list of cgroup hierarchies you want to use. `all` will use all hierarchies supported by the library.
This parameter will be ignored if the cgroup already exists (all existing hierarchies will be used).

*user* is the cgroups sub-directories name to use (NOT SURE WHAT YOU MEAN TO SAY WITH THIS SENTENCE. Could you clarify what you are trying to convey for me?). `current` will use the name of the current user.

```python
from cgroups import Cgroup

cg = Cgroup('charlie')
```


**Cgroup.add(pid)**

Add the process to all hierarchies within the cgroup.

*pid* is the pid of the process you want to add to the cgroup.

```python
from cgroups import Cgroup

cg = Cgroup('charlie')
cg.add(27033)
```

If *pid* is already in cgroup hierarchy, this function will fail silently.

*N.B*: For security reasons the process has to belong to user if you execute this code as a non-root user.


**Cgroup.remove(pid)**

Remove the process from all hierarchies within the cgroup.

*pid* is the pid of the process you want to remove from the cgroup.

```python
from cgroups import Cgroup

cg = Cgroup('charlie')
cg.remove(27033)
```

If *pid* is not in the cgroup hierarchy this function will fail silently.

*N.B*: For security reasons the process has to belong to user if you execute this code as a non-root user.


**Cgroup.set_cpu_limit(limit)**

Set the cpu limit for the cgroup.
This function uses the `cpu.shares` hierarchy.

*limit* is the limit you want to set (as a percentage).
If you don't provide an argument to this method, the menthod will set the cpu limit to the default cpu limit (ie. no limit).

```python
from cgroups import Cgroup

cg = Cgroup('charlie')

# Give the cgroup 'charlie' 10% limit of the cpu capacity
cg.set_cpu_limit(10)

# Reset the limit
cg.set_cpu_limit()
```


**Cgroup.cpu_limit**

Get the cpu limit of the cgroup as a percentage.


**Cgroup.set_memory_limit(limit, unit='megabytes')**

Set the memory limit of the cgroup (including file cache but exluding swap).
This function uses the `memory.limit_in_bytes` hierarchy.

*limit* is the limit you want to set.
If you don't provide an argument to this method, the menthod will set the memory limit to the default memory limit (ie. no limit)

*unit* is the unit used for the limit. Available choices are 'bytes', 'kilobytes', 'megabytes' and 'gigabytes'. Default is 'megabytes'.


```python
from cgroups import Cgroup

cg = Cgroup('charlie')

# Give the cgroup 'charlie' a maximum memory of 50 Mo.
cg.set_memory_limit(50)

# Reset the limit
cg.set_memory_limit('charlie')
```


**Cgroup.memory_limit**

Get the memory limit of the the cgroup in megabytes.


**Cgroup.delete()**

Delete the cgroup.

*N.B*: If there are any processes in the cgroup, they will be moved into the user's cgroup sub-directories.

```python
from cgroups import Cgroup

cg = Cgroup('charlie')
cg.delete()
```
