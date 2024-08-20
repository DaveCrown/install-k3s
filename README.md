
# Installs a K3s Cluster

## Description

This play installs a Kubernetes cluster using k3's on one master node and how ever many workers you define. I developed this for my home environment and making it easier to redeploy a k3s cluster on raspbery pi's.  The play is fairly idempotent, as it uses the presence of the node-token file and agent uninstall script to detect if you have k3's install

## Requiremnets
Right now I'm only targeting ubuntu. There are no guard rails to stop this from running on other distributions. I make the assumption of a single master and multiple workers.

## Usage

> [!Caution] A word on cluster secrets
> Since this play is meant for a home lab, it will copy the default k3s.yml and node-node token to a directory called work while the play is 

### Installation
To use the installation play:
1. build your inventory out
1. call `ansible-play install-k3s.yml -e '{ any flags here in json format }'`
1. get a cup of coffee

I use `ansible-playbook install-k3s.yml -e '{ "build_config": true, "install_u6143": true}' `

### Uninstall
This is pretty simple, just call the `uninstall-k3s.yml` play like so. It will also remove most of the on disk configs

`ansible-playbook uninstall-k3s.yml`

### Prereqs
This will do the following:
- Set the hostname of each node to whats defined in the inventory
- Create a service account with the following defaults
     - a user name of ansible
     - the ssh key of id_ed25519.pub
     - no sudo password
- Install the following:
[!INCLUDE [./prep_hosts/vars/main.yml](prep_hosts/vars/main.yml)]

To manage this, use the flags in the [CLI Section](#CLI)

## Inventory

### Nodes
This section has two groups, master and workers. Its expected that you use names for the nodes as it updates nodes hostname to the node name defined in the inventory file for the sake of making it wasier to work with k8s. 

As I'm planing to expand this to apply inital configs of the cluster, please leave the `nodes:children` intact.

```ini
[master]
master_node_name ansible_host=host

[workers]
worker1_node_name ansible_host=host
worker2_node_name ansible_host=host
...
workerN_node_name ansible_host=host

[nodes:children]
master
workers
```

## Vars

### CLI
| Option | Type| Usage | Default | Notes|
| --- | --- | --- | --- | --- |
| manage_service_account | bool | should the play manage service account for thenodes os| `true` | |
| service_account_name | string | name of the account | `ansibe`| |
| service_account_nopasswd | bool | whether to allow passwdless sudo | `true` | since this is for home labs, I keep this to true. feel free to set a password and store it an ansible vault for later. |
| ssh_key_file | string | what ssh key to configure | `id_ed25519.pub` |
| install_u6143 | bool |Install a utronics u6143 driver for raspberry pi's | `false` | see the docs on the [Utronics site](https://www.uctronics.com/download/Amazon/U6145_Manual.pdf) |
| build-config | bool | should the play replace ~/.kube/config with ne from the new cluster | `false` | leave disabled if you want to merge the new cluster config into your `.kube/config` |
| install_prereqs | bool | should the play install the prereqs and prep the nodes | `true` | does a little more than installing prereuqes. See the [PreReqs Secions](#Prereqs) |

### Main Vars

In the play there are a few main vars
| Option| Usage | Notes |
| --- | --- | --- |
| master_node | The name of the master node | will replace with lookup function later |
| disable_k3s_plugins | A list of k3s plugins to disable | servicelb and traefik are disabled to i can install metallb and ingress-nginx |

## To do's
On my list is to include deploying and configuring:
 - ingress-nginx
 - metallb
 - dynamic nfs PVC provsioner

## Legal
I am in no away affiliated with any company , nor did I write the fix. I just wrote an ansible play making deploying a home lab easier and share it with the world. Use this as your own peril with good backups. Don't blame me if this burns down your environment, your house, or anything you were warned. I take no responsibility or liability.

Trademarks and Copyrights are properties of their respective owners.