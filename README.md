# cgroups

*cgroups* is a library to use and manage cgroups in python.

## Installation

```bash
	pip install cgroups
```

`cgroups` works only on Linux systems, with a recent kernel and the cgroups filesystem mounted (which is the case of most Linux distributions since 2012).

**Non-root**

In order to allow non-root user to manage cgroups you have to execute first the `cgroup_user` command.

Assuming you use `sudo`:

```bash
	sudo cgroup_user -u USER
```

If you don't specify `USER` it will use the current user.

*N.B.*: This will only give the user permissions to manage cgroups in it's own sub-group. It wiil not give him permissions on other cgroups or system commands.


## Usage

**cgroups.create(name)**

Create a new cgroup.
This function create the new cgroup in the following hierarchy: `cpu`, `memory`.

*name* is the name of the new cgroup that will be created.

```python

	import cgroups

	cgroups.create('charlie')
```


**cgroups.add(name, pid)**

Add a process to an existing cgroup.
This function add the process to all the hierarchy of the cgroup.

*name* is the name of the cgroup.

*pid* is the pid of the process you want to add in the cgroup.

```python

	import cgroups

	cgroups.add_process('charlie', 27033)
```

If *pid* is already in cgroup hierarchy, this function will fail silently.

*N.B*: For security reasons the process has to belong to user if you execute as a non-root user.


**cgroups.remove(name, pid)**

Remove a process to an existing cgroup.
This function remove the process from all the hierarchy of the cgroup.

*name* is the name of the cgroup.

*pid* is the pid of the process you want to add in the cgroup.

```python

	import cgroups

	cgroups.remove_process('charlie', 27033)
```

If *pid* is not in cgroup hierarchy, this function will fail silently.

*N.B*: For security reasons the process has to belong to user if you execute as a non-root user.

**cgroups.cpu_limit(name, limit)**

Set a cpu limit to an existing cgroup.
This function use the `cpu.shares` hierarchy.

*name* is the name of the cgroup.

*limit* is the limit you want to set, in pourcentage.
If you don't specify a value it will reset to the default (ie. no limit).

```python

	import cgroups

	# Give the cgroup 'charlie' 10% of the cpu capacity
	cgroups.cpu_limit('charlie', 10)

	# Reset the limit
	cgroups.cpu_limit('charlie')
```


**cgroups.memory_limit(name, limit, unit='megabytes')**

Set a memory limit to an existing cgroup (including file cache but exluding swap).
This function use the `memory.limit_in_bytes` or the `memory.memsw.limit_in_bytes` hierarchy.

*name* is the name of the cgroup.

*limit* is the limit you want to set.
If you don't specify a value it will reset to the default (ie. no limit).

*unit* is the unit used for the limit. Available choices are 'bytes', 'kilobytes', 'megabytes' and 'gigabytes'. Default is 'megabytes'.


```python

	import cgroups

	# Give the cgroup 'charlie' a maximum memory of 50 Mo.
	cgroups.mem_limit('charlie', 50)

	# Reset the limit
	cgroups.mem_limit('charlie')
```


**cgroups.delete(name)**

Delete an existing cgroup.

*name* is the name of the new cgroup that will be created.

*N.B*: If there is still process in this cgroups, they will be moved to the user root cgroup.

```python

	import cgroups

	cgroups.delete('charlie')
```
