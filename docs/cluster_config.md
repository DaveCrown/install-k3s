# Cluster Config reference

## Description
To make this play a little more portable, this uses cluster config thats stored in separate repository or directory of your choosing.

## Format

Right now, the file has the config for the master node, as well as any plugins to install. The plugins are defined in the `plugin_map.yaml` file. Plugins can be either manifest or helm charts. While defined elsewhere, we use this file to load them. See the [plugin_map.md](plugin_map.md) file for details on this file. 

```yml
master_node: <master node as defined in the inventory>

plugins:
  - plugin: <manifest plugin name>
    config_file: <additional manifest(s) to apply. the path is relative to the root of the config dir/repo>

  - plugin: <name of a helm based plugin>
    name: <name to use for the release>
    namespace: <namespace to create>
    config_file: <name of the values file to pass to helm, path relative to the root of the config dir/repo>
```
### Manifest options
| Name | Value | Notes |
| --- | --- | --- |
| plugin| Name of the plugin to use | These are defined in the plugin map file | 
| config_file| additional yaml file to apply after the plugin has been installed | file name is relative tot he root of the directory/repo  |

### Helm Chart Options
| Name | Value | Notes |
| --- | --- | --- |
| plugin| Name of the plugin to use | These are defined in the plugin map file | 
| config_file| athe name of the halm values to deploy your helm chart | file name is relative tot he root of the directory/repo |
| name | the name for the release to helm to build out | |
| namespace | name space to create and deploy the plugin to | defaults to name |