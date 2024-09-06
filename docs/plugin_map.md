# Plugin Map reference

## Description
To allow for a more for a config driven cluster boot strap, I need to provide a menu and mapping to feed data into the install and configure plays. `plugin_map.yaml` contains the static data used to marry with the cluster config. The file itself is stored at the root of the play.  

## Format

Just like the cluster config, this file supports two kinds of plugins, manifest and helm, and both can be defined along side of each other.

The inbox section is the plugins that come with K3's. This is used to validated the `disables` option


```yml
---
plugins:
  <Plugin Name>: #manifest based install
    kind: manifest
    manifests:
      - <url of manifest>
    disables: 
      - <inbox plugins to disable>

  <Plugin Name>: #helm based install
    kind: helm
    repo: <url of helm repo>
    chart: <chart name>
    disables: 
      - <inbox plugins to disable>

in_box:
  - traefik
  - servicelb
  - flannel
  - coredns
  
```

### Manifest options
| Name | Value | Notes |
| --- | --- | --- |
| \<plugin name \>| Name of the plugin | This is what the `plugin` field in the `cluster_config.yaml` files refrences |
| kind | `manifest` | used to specify a manifest based install
| manifests | a list of manifests/crd's/ etc to be applied  | pretty much any thing that gets used with a `kubectl apply -f` |
| disables | a list of in box plugins to disable | use this when your plugin is replacing an in box one, i.e. Metal LB for Service LB |

### Helm Chart Options
| Name | Value | Notes |
| --- | --- | --- |
| \<plugin name \>| Name of the plugin | This is what the `plugin` field in the `cluster_config.yaml` files refrences |
| kind | `helm` | this is used to specified  |
| name | the name for the release to helm to build out | |
| namespace | name space to create and deploy the plugin to | defaults to name |
| disables | a list of in box plugins to disable | use this when your plugin is replacing an in box one, i.e. Metal LB for Service LB |