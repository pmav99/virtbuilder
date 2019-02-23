# 3 Ubuntu 18.04 VMs ready for ansible

This example creates 3 VMs in their own network.
The VMs are running Ubuntu 18.04 and they are "ansible-ready" (i.e. they have python
installed).

## Quickstart

``` bash
virsh --connect qemu:///system net-create test-network.xml
virsh --connect qemu:///system pool-define-as test-pool dir - - - - $XDG_DATA_HOME/libvirt/pools/test-pool
virsh --connect qemu:///system pool-build     test-pool
virsh --connect qemu:///system pool-start     test-pool
virtbuilder multi create node1.yml node2.yml node3.yml -n
```


## Topology

```
 hostname           IP
-----------     ---------
test-master     10.10.10.10
test-node1      10.10.10.11
test-node2      10.10.10.12
```


## Credentials

The root password is defined in `data/root_password.txt`. The default password is `1234`
but you may change that. Or you can disable it completely. For more info please consult
`virt-builder`'s docs.

Your ssh public key (`$HOME/.ssh/id_rsa.pub`) is also being injected into the root
account. If you want to use a different key, please edit the definition files.

## Create the VMs

### Create the network

We first need to create the network. To keep things simple, we have already created the
network definition in `test-network.xml` and we can create it with:

``` bash
virsh --connect qemu:///system net-create test-network.xml
```

This will create a new network bridge named `virbr-test`. You can inspect the bridge with:

```
brctl show
```

You can also inspect the network with:

```
virsh --connect qemu:///system net-list --all
```

### Create the pool

In order to keep things simple and tidy, it is a good idea to keep your VM images inside
a pool. Our definition files expect to be stored in a pool named `test-pool`. So, let's
create it:

``` bash
virsh --connect qemu:///system pool-define-as test-pool dir - - - - $XDG_DATA_HOME/libvirt/pools/test-pool
virsh --connect qemu:///system pool-build     test-pool
virsh --connect qemu:///system pool-start     test-pool
```

### Create the nodes

You can finally create the nodes

``` bash
virtbuilder create node1.yml -n
virtbuilder create node2.yml -n
virtbuilder create node3.yml -n
```

Alternatively you can run:

```
virtbuilder multi create node1.yml node2.yml node3.yml -n
```

The first node might take some time, because `virt-builder` will download the base image
from Redhat's servers, but the next two shouldn't take more than a minute (on an SSD and
a reasonably fast internet connection).

You can check that the VMs have been create with:

```
virsh --connect qemu:///system list --all
```

You should see something like this:

```
 Id   Name                 State
-------------------------------------
 1    test-node1           running
 2    test-node2           running
 3    test-node3           running
```

## Test ansible

You can now test if ansible is working:

``` bash
ansible all -mping
ansible masters -mping
ansible nodes -mping
```

## Test SSH

You can also test to connect via SSH

``` bash
ssh root@test-node1
ssh root@test-node2
ssh root@test-node3
```

If name resolution is not working you need to setup NSS to use the libvirt addons. For
more info please read
[here](https://lukas.zapletalovi.com/2017/10/definitive-solution-to-libvirt-guest-naming.html)
In the meantime you can use the IPs:

``` bash
ssh root@10.0.0.10
ssh root@10.0.0.11
ssh root@10.0.0.12
```

You can also check the DHCP leases:
``` bash
virsh --connect qemu:///system net-dhcp-leases test-network
```


## Cleaning up

```
virtbuilder multi remove node1.yml node2.yml node3.yml -n
virsh --connect qemu:///system net-destroy test-network
virsh --connect qemu:///system pool-destroy test-pool
virsh --connect qemu:///system pool-delete test-pool
virsh --connect qemu:///system pool-undefine test-pool
```
