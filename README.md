
# Installs and Configures a K3s Cluster

## Description

This play installs and configures a Kubernetes  cluster using k3's on one master node and how ever many workers you define. I developed this for my home environment and making it easier to redeploy a k3s cluster on raspbery pi's.  The play is fairly idempotent, as it uses the presence of the node-token file and agent uninstall script to detect if you have k3's installed.  The play will also configure the cluster's initial plugins for your cluster, provding consistent and *as code* setup.

## Requirements

Right now I'm only targeting ubuntu. There are no guard rails to stop this from running on other distributions. I make the assumption of a single master and multiple workers.

## Usage

> [!CAUTION]  
>
> Since this play is meant for a home lab, it will copy the default k3s.yml and node-node token to a directory called work while the play is running. While the play will delete work dir when done, it still creates some exposure. You have been thusly warned. 

### Installation

To use the installation play:
1. build your inventory out
1. (Optionaly) Make sure you have your cluster_config.yaml and config directory built out
1. call `ansible-play configure-k3s.yml -e '{ any flags here in json format }'`
1. get a cup of coffee

I use `ansible-playbook install-k3s.yml -e '{ "build_config": true, "install_u6143": true, "config_repo": some git url}'`

### Configuration
To use the installation play:
1. Make sure you have your cluster_config.yaml and config directory built out 
1. call `ansible-play install-k3s.yml -e '{ any flags here in json format }'`
1. get a cup of coffee

I use `ansible-playbook configure-k3s.yml -e '{ "config_repo": some git url}'`

### Uninstall

> [!CAUTION]  
>
> This will remove K3's from you cluster and any configuation files on the nodes.

This is pretty simple, just call the `uninstall-k3s.yml` play like so. It will also remove most of the on disk configs.

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

This section has two groups, master and workers. Its expected that you use names for the nodes as it updates nodes hostname to the node name defined in the inventory file for the sake of making it easier to work with k8s. 

Please leave the `nodes:children` intact as this is for planned future functionality.

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

## Config Files 
To Configure your cluster with the plugins required for bootstrapping a home lab the play uses two files, `cluster_config.yaml`([docs](docs/cluster_config.md)) and `plugin_map.yaml`([docs](docs/plugin_map.md)). 

- `cluster_config.yaml` ([docs](docs/cluster_config.md)) needs to be in a local directory or git repo along with any other manifests and and helm chart value files you need to boot strap your environement. The idea is two fold. The first being it makes it easy to keep the bootstraping *as code*. The second is you could extend this play to multiple clusters.
- `plugin_map.md` ([docs](docs/plugin_map.md)) is at the root of the this repo. As as this file contains the more static definitions used for `cluster_config.yaml` I've included it in this play.

I've included some [sample files](sample_files/), though you will need to adjust some of the files if you want to use them. 

### CLI

| Option | Type| Usage | Default | Notes|
| --- | --- | --- | --- | --- |
| manage_service_account | bool | should the play manage service account for thenodes os| `true` | |
| service_account_name | string | name of the account | `ansible`| |
| service_account_nopasswd | bool | whether to allow passwdless sudo | `true` | since this is for home labs, I keep this to true. feel free to set a password and store it an ansible vault for later. |
| ssh_key_file | string | what ssh key to configure | `id_ed25519.pub` |
| install_u6143 | bool |Install a utronics u6143 driver for raspberry pi's | `false` | see the docs on the [Utronics site](https://www.uctronics.com/download/Amazon/U6145_Manual.pdf) |
| build-config | bool | should the play replace ~/.kube/config with ne from the new cluster | `false` | leave disabled if you want to merge the new cluster config into your `.kube/config` |
| install_prereqs | bool | should the play install the prereqs and prep the nodes | `true` | does a little more than installing prereuqes. See the [PreReqs Secions](#Prereqs) |
| config_dir | string | Where should the play pull the cluster's config from | `none` | This will result in copying the directory with your config files and load them into the play. Its mutually exclusive with `config_repo` |
| config_repo | string | The location of a gir repo to clone and use for configuration | `none` | This will cause the play to clone in a repo and load them into the play. Its mutually exclusive with `config_dir` |

### Main Vars

In the play there are a few main vars
| Option| Usage | Notes |
| --- | --- | --- |
| master_node | The name of the master node | will replace with lookup function later |
| disable_k3s_plugins | A list of k3s plugins to disable | servicelb and traefik are disabled to i can install metallb and ingress-nginx |

## Relese notes

### 1.0 
- Initial Release

### 1.1
- Replaced static plugin disablement with a dynamic system
- Added the `config.yml` to install the set of plugins for the cluster
- included a custom jinja2 filter to make parsing the data model easier 

## To do's

- [] Install / Deploy / Configure the following
  - [x] ingress-nginx
  - [x] metallb
  - [x] dynamic nfs PVC provisioner
- [ ] Vagrant file
- [ ] Test Coverage
- [ ] Document how to pull from a private repo when used with tower
- [X] Move this to github issues

## Legal
I am in no away affiliated with any company , nor did I write the fix. I just wrote an ansible play making deploying a home lab easier and share it with the world. Use this as your own peril with good backups. Don't blame me if this burns down your environment, your house, or anything you were warned. I take no responsibility or liability.

Trademarks and Copyrights are properties of their respective owners.