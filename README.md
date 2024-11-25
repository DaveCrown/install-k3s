
# Installs and Configures a K3s Cluster

## Description

This project proves a few plays for installing and managing a k3s cluster. I wrote this make redeploying and managing my home lab easier. To make this reusable modular, and extensible, the project uses an external config that can be brought in via directory or git repo. The project is comprised of a few plays. To keep the install and uninstall plays idempotent, they validate the the installation via a token file and uninstall binary to determine if K3's is installed. 

### Plays in this project

- `install-k3s.yml`:  The install play will install any pre-req packages and install the control and worker nodes.
- `configure-k3s.yaml`: This play will manage boot strapping of the cluster and install and configure things like loadbalencers and CNI's/CSI's/Etc and matching manifests. 
- `uninstall.yml`: This play removes K3s and any on node artifcats
- `node-maintenance`: This play will ensure the pre-reqs are installed and then patch the nodes. If it detects a reboot is required, it will drain and reboot nodes one at a time. 

## Requirements

Right now I'm only targeting ubuntu. There are no guard rails to stop this from running on other distributions. I make the assumption of a single master and multiple workers. To ensure you have all the proper collections installed, please run `ansible-galaxy install -r requirements.yml`

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
1. Call `ansible-play install-k3s.yml -e '{ any flags here in json format }'`
1. Get a cup of coffee

I use `ansible-playbook configure-k3s.yml -e '{ "config_repo": some git url}'`

### OS Patching / Maintenance  

With all the automation I have going on with this project, OS management should be included. The `node-maintenance.yml' play will do a few things. The idea is to use this play to reconverge your node while doing your OS maintenance.

1. Ensure the packages required are present on the nodes
1. Patch each node via dist upgrade
1. Remove any packages marked as unneeded
1. Perform a rolling Drain, reboot, and uncordon nodes if a reboot is required. Reboot is governed by the preense of `/var/run/reboot-required`

The play uses some of the same flags as the install as documented below, however, I use use `ansible-playbook node-maintenance.yml -e '{ "install_u6143": true}'`

### Uninstall

> [!CAUTION]
>
> This will remove K3's from you cluster and any configuration files on the nodes.

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
  - `git`
  - `raspi-config`
  - `build-essential`
  - `nfs-common`
  - `net-tools`
  - `htop`
- Removes:
  - `prometheus-node-exporter`

To manage this, use the flags in the [CLI Section](#cli)

#### Prometheus

In the version 1.2 of the play, I added support for installing Prometheus to the K3's cluster. I'm using the the community stack to deploy Prometheus, Grafana, and Alert Manager. If the Prometheus plugin is enabled, the play will remove `prometheus-node-exporter` from the nodes the Prep Hosts phase.

Configuring Prometheus is beyond the scope of this documentation.

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

#### install-k3s

| Option | Type| Usage | Default | Notes|
| --- | --- | --- | --- | --- |
| manage_service_account | bool | should the play manage service account for the nodes os| `true` | |
| service_account_name | string | name of the account | `ansible`| |
| service_account_nopasswd | bool | whether to allow passwdless sudo | `true` | since this is for home labs, I keep this to true. feel free to set a password and store it an ansible vault for later. |
| ssh_key_file | string | what ssh key to configure | `id_ed25519.pub` | |
| install_u6143 | bool |Install a utronics u6143 driver for raspberry pi's | `false` | see the docs on the [Utronics site](https://www.uctronics.com/download/Amazon/U6145_Manual.pdf) |
| build-config | bool | should the play replace ~/.kube/config with ne from the new cluster | `false` | leave disabled if you want to merge the new cluster config into your `.kube/config` |
| install_prereqs | bool | should the play install the prereqs and prep the nodes | `true` | does a little more than installing prereqs. See the [Prereqs Secions](#prereqs) |
| config_dir | string | Where should the play pull the cluster's config from | `none` | This will result in copying the directory with your config files and load them into the play. Its mutually exclusive with `config_repo` |
| config_repo | string | The location of a gir repo to clone and use for configuration | `none` | This will cause the play to clone in a repo and load them into the play. Its mutually exclusive with `config_dir` |
| patch_everything | bool | whether or not to run `apt update && apt upgrade -y` | `false` | |

#### configure-k3s
| Option | Type| Usage | Default | Notes|
| --- | --- | --- | --- | --- |
| config_dir | string | Where should the play pull the cluster's config from | `none` | This will result in copying the directory with your config files and load them into the play. Its mutually exclusive with `config_repo` |
| config_repo | string | The location of a gir repo to clone and use for configuration | `none` | This will cause the play to clone in a repo and load them into the play. Its mutually exclusive with `config_dir` |

#### node-maintenance
| Option | Type| Usage | Default | Notes|
| --- | --- | --- | --- | --- |
| manage_service_account | bool | should the play manage service account for the nodes os| `true` | |
| service_account_name | string | name of the account | `ansible`| |
| service_account_nopasswd | bool | whether to allow passwdless sudo | `true` | since this is for home labs, I keep this to true. feel free to set a password and store it an ansible vault for later. |
| ssh_key_file | string | what ssh key to configure | `id_ed25519.pub` | |
| install_u6143 | bool |Install a utronics u6143 driver for raspberry pi's | `false` | see the docs on the [Utronics site](https://www.uctronics.com/download/Amazon/U6145_Manual.pdf) |

## Release notes

### 1.0

- Initial Release

### 1.1

- Replaced static plugin disablement with a dynamic system
- Added the `config.yml` to install the set of plugins for the cluster
- included a custom jinja2 filter to make parsing the data model easier

### 1.2

- Added support for Prometheus
- Made `apt update && apt upgrade -y` optional

### 1.2.1

- Fixed Prometheus support:
  - Remove packages if selected
  - added support for CRD's
- Added sloth support
- Added pre-req support. If sloth requires prometheus, validated prometheus is also selected.
- refactored the configure play into a role for readability
- various fixes to make the linter happy
- added devcontainer support to work around PyYAML support with homebrew and Python 3.13

# 1.3

- Added a play to patch and reboot the nodes
- moved patching from install to maint play
- included prep_hosts and install_u6143 in maint play
- moved build packages to the the install_u6143 role
- changed the install u6143 role to use the make module instead of command

## To do's

- [x] Install / Deploy / Configure the following
  - [x] ingress-nginx
  - [x] metallb
  - [x] dynamic nfs PVC provisioner
- [ ] Vagrant file
- [ ] Test Coverage
- [ ] Document how to pull from a private repo when used with tower
- [X] Move this to github issues

## Legal

I am in no away affiliated with any company, nor did I write any of the software being deployed with this. I just wrote an ansible play making deploying a home lab easier and shared it with the world. Use this as your own peril with good backups. Don't blame me if this burns down your environment, your house, or anything... you were warned. I take no responsibility or liability.

Trademarks and Copyrights are properties of their respective owners.
