# cgroups

*cgroups* is a library to use and manage Linux kernel feature cgroups.

For now the library only handle `cpu` and `memory`cgroups.


## Installation

```bash
	pip install cgroups
```

`cgroups` feature works only on Linux systems, with a recent kernel and the cgroups filesystem mounted on `/sys/fs/cgroup` (which is the case of most Linux distributions since 2012).

**Root and non-root**

To use *cgroups* the current user as to have root privileges OR existing cgroups sub-directories.

In order to create those cgroups sub-directories you can execute with root privileges the `cgroup_user` command.

Assuming you use `sudo`:

```bash
	sudo user_cgroups USER
```

*N.B.*: This will only give to the user permissions to manage cgroups in it's own sub-directories and it's own process. It wiil not give him permissions on other cgroups, other process or system commands.

*N.B.*: You have to execute this script only once.


## Usage

**class Cgroup(name, hierarchies='all')**

Create or load a cgroup.

*name* is the name of the cgroup.

*hierarchies* is a list of cgroup hierarchies you want to use. `all` will use all hierarchies supported by the library.
This parameter will be ignored if the cgroup already exists (all existing hierarchies will be used).

```python

	from cgroups import Cgroup

	cg = Cgroup('charlie')
```


**Cgroup.add(pid)**

Add the process to all hierarchies of the cgroup.

*pid* is the pid of the process you want to add to the cgroup.

```python

	from cgroups import Cgroup

	cg = Cgroup('charlie')
	cg.add(27033)
```

If *pid* is already in cgroup hierarchy, this function will fail silently.

*N.B*: For security reasons the process has to belong to user if you execute as a non-root user.


**Cgroup.remove(pid)**

Remove the process to all hierarchies of the cgroup.

*pid* is the pid of the process you want to remove of the cgroup.

```python

	from cgroups import Cgroup

	cg = Cgroup('charlie')
	cg.remove(27033)
```

If *pid* is not in cgroup hierarchy, this function will fail silently.

*N.B*: For security reasons the process has to belong to user if you execute as a non-root user.


**Cgroup.set_cpu_limit(limit)**

Set the cpu limit to the cgroup.
This function use the `cpu.shares` hierarchy.

*limit* is the limit you want to set, in pourcentage.
If you don't specify a value it will reset to the default (ie. no limit).

```python

	from cgroups import Cgroup

	cg = Cgroup('charlie')

	# Give the cgroup 'charlie' 10% limit of the cpu capacity
	cg.set_cpu_limit(10)

	# Reset the limit
	cg.set_cpu_limit()
```


**Cgroup.cpu_limit**

Get the cpu limit of the the cgroup in pourcentage.


**Cgroup.set_memory_limit(limit, unit='megabytes')**

Set the memory limit of the cgroup (including file cache but exluding swap).
This function use the `memory.limit_in_bytes` hierarchy.

*limit* is the limit you want to set.
If you don't specify a value it will reset to the default (ie. no limit).

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

*N.B*: If there is still process in the cgroup, they will be moved to the user cgroup sub-directories.

```python

	from cgroups import Cgroup

	cg = Cgroup('charlie')
	cg.delete()
```
