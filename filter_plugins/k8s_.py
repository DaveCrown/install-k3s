#!/usr/bin/env python3
"""This is my library of custom jinja filters. 

    by implementing the complex logic in python, i can i avoid having jinja statements that look like obfuscated perl
"""


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    # if/when i put a play to bootstrap an environment, putting my imports in a try/catch will allow the bootstrap to run successfully  
    # the down side is that an improperly configured python environment will result in an empty result because this failed silently 
    # the reason is that ansible will load all filter plugins whether they are needed or not. so a bootstrap play and custom jinja plugin will cause the bootstrap to fail.
    from jinja2 import TemplateError
    #from ansible.module_utils._text import to_text
except:
    pass

class FilterModule(object):
    def get_enabled_plugins(self,config:dict, plugin_map:dict)->list:
        """Takes the configfile and plugin map, and return a list of plugins to bwe enabled. The primary purpose for this is validating of a plugin is selected to install,
           i.e. install prometheus node exporter if the prometheus is an enabled plugin. 

        Usage: {{ config | get_enabled_plugins(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Returns:
            list: a list with plugins to be enabled.
       """

        enabled_plugins = set()

        all_plugins = set(plugin_map['plugins'].keys())
        for config_plugin in config['plugins']:
            enabled_plugins.add(config_plugin['plugin'])

        enabled_plugins = enabled_plugins & all_plugins

        return list(enabled_plugins)

    def get_disables(self,config:dict,plugin_map:dict)->list:
        """will take a config file in the defined format and config plugin map and generate a list of plugins to disable

        Usage: {{ config | get_disables(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Returns:
            list: a list with the plugins to disable
        """

        disable_list = set()
        disable_args = ""
        for config_plugin in config['plugins']:
            if config_plugin['plugin'] not in plugin_map['plugins']:
                raise TemplateError("Undefined Plugin: {} found".format(config_plugin['plugin']))

            plugin_def= plugin_map['plugins'][config_plugin['plugin']]

            if 'disables' in plugin_def and  plugin_def['disables'] is not None:
                disable_list = disable_list.union(plugin_def['disables'])

        if len(disable_list) > 0:
            for arg in disable_list:
                disable_args += "--disable {} ".format(arg)
        
        return disable_args


    def get_manifests(self,config:dict,plugin_map:dict)->list:
        """Takes the config file and plugin map and generates a list of manifests to apply

        Usage: {{ config | get_manifests(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Raises:
            TemplateError: An error if an undefined plugin is used
            TemplateError: An error if manifest is not a list

        Returns:
            list: a list of manifests to apply
        """
        manifest_list = set()

        for config_plugin in config['plugins']:
            if config_plugin['plugin'] not in plugin_map['plugins']:
                raise TemplateError("Undefined Plugin: {} found".format(config_plugin['plugin']))

            plugin_def= plugin_map['plugins'][config_plugin['plugin']]
            if 'kind' in plugin_def and plugin_def['kind'] == "manifest":
                if not isinstance(plugin_def['manifests'],list):
                    raise TemplateError("Plugin {} manifest must be of type list".format(config_plugin['plugin']))
                manifest_list = manifest_list.union(plugin_def['manifests'])

        return list(manifest_list)

    def get_manifest_configs(self,config:dict,plugin_map:dict)->list:
        """Takes the config file and plugin map and generates a list of extra manifests to apply afterwards

        Usage: {{ config | get_manifests_configs(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Raises:
            TemplateError: An error if an undefined plugin is used

        Returns:
            list: a list of extra manifests to apply after the manifest based plugins are installed
        """

        manifest_list = []
        for config_plugin in config['plugins']:
            if config_plugin['plugin'] not in plugin_map['plugins']:
                raise TemplateError("Undefined Plugin: {} found".format(config_plugin['plugin']))

            plugin_def= plugin_map['plugins'][config_plugin['plugin']]
            if 'kind' in plugin_def and plugin_def['kind'] == "manifest":
                manifest_list.append(config_plugin['config_file'])
        
        return manifest_list
    
    def get_manifest_namespaces(self,config,plugin_map)->list:
        """Takes the config file and plugin map and generates a list of name spaces to create in advance of install the manifests

        Usage: {{ config | get_get_manifest_namespaces(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Raises:
            TemplateError: An error if an undefined plugin is used

        Returns:
            list: a list of namespaces to create
        """
        namespace_list = []
        for config_plugin in config['plugins']:
            if config_plugin['plugin'] not in plugin_map['plugins']:
                raise TemplateError("Undefined Plugin: {} found".format(config_plugin['plugin']))

            plugin_def= plugin_map['plugins'][config_plugin['plugin']]
            if 'kind' in plugin_def and plugin_def['kind'] == "manifest" and 'namespace' in config_plugin:
                if config_plugin['namespace'] not in namespace_list:
                    namespace_list.append(config_plugin['namespace'])
        return namespace_list

    def get_helm_repos(self,config:dict,plugin_map:dict)->list:
        """Takes the config file and plugin map and creates a list of helm repositories to add

        Usage: {{ config | get_helm_repos(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Raises:
            TemplateError: An error if an undefined plugin is used

        Returns:
            list: a list of helm repositories 
        """
        repos = {}
        full_repo_list = []

        for config_plugin in config['plugins']:
            if config_plugin['plugin'] not in plugin_map['plugins']:
                raise TemplateError("Undefined Plugin: {} found".format(config_plugin['plugin']))

            plugin_def= plugin_map['plugins'][config_plugin['plugin']]
            if 'kind' in plugin_def and plugin_def['kind'] == "helm":
                if 'repo' in plugin_def and isinstance(plugin_def['repo'],str) and config_plugin['plugin'] not in repos:
                    repos[config_plugin['plugin']] = plugin_def['repo']

        return repos

    def get_helm_namespaces(self,config,plugin_map)->list:
        """Takes the config file and plugin map and generates a list of name spaces to create in advance of install the releases

        Usage: {{ config | get_helm_repos(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Raises:
            TemplateError: An error if an undefined plugin is used

        Returns:
            list: a list of namespaces
        """
        namespace_list = []
        for config_plugin in config['plugins']:
            if config_plugin['plugin'] not in plugin_map['plugins']:
                raise TemplateError("Undefined Plugin: {} found".format(config_plugin['plugin']))

            plugin_def= plugin_map['plugins'][config_plugin['plugin']]
            if 'kind' in plugin_def and plugin_def['kind'] == "helm" and 'namespace' in config_plugin:
                if config_plugin['namespace'] not in namespace_list:
                    namespace_list.append(config_plugin['namespace'])
        return namespace_list

    def get_helm_charts(self,config:dict,plugin_map:dict,top_dir:str)->list:
        """Takes the config file and plugin map and generates a list of dicts of helm charts to apply

        Usage: {{ config | get_helm_charts(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map
            top_dir (str): the directory on disk where the play is running from. you should pass in playbook_dir to the filter at invocation

        Raises:
            TemplateError: An error if an undefined plugin is used

        Returns:
            list: A list of dicts with the necessary data to install the required helm charts
        """

        helm_charts = []

        for config_plugin in config['plugins']:
            chart = {}
            chart['files']=[]
            if config_plugin['plugin'] not in plugin_map['plugins']:
                raise TemplateError("Undefined Plugin: {} found".format(config_plugin['plugin']))

            plugin_def= plugin_map['plugins'][config_plugin['plugin']]
            if 'kind' in plugin_def and plugin_def['kind'] == "helm":
                chart['name'] = config_plugin['name']
                chart['namespace'] = config_plugin['namespace']
                chart['ref'] = plugin_def['chart']
                if 'config_file' in config_plugin:
                    chart['files'].append(top_dir + '/config/' + config_plugin['config_file'])
                helm_charts.append(chart)

        return helm_charts

    def validate_prereqs(self,config:dict,plugin_map:dict)->bool:
        """This filter will parse the config and plugin map and validate that all plugins that any plugin prereq is satisfied. 
        I.E. if sloth is selected and it has a prereq of prometheus, that prometheus is also selected. 

        Usage: {{ config | validate_prereqs(plugin_map) }}

        Args:
            config (dict): this is a imported config file of what to configure at install
            plugin_map (dict): the object with the plugin map

        Returns:
            bool: true if all the prereqs are met. 
        """

        met_prereqs = False
        required_plugins=set()

        enabled_plugins = set(self.get_enabled_plugins(config,plugin_map))

        for enabled_plugin in enabled_plugins:
            plugin_def= plugin_map['plugins'][enabled_plugin]
            if 'requires' in plugin_def:
                required_plugins = required_plugins.union(set(plugin_def['requires']))
        
        if len(required_plugins) == 0:
            met_prereqs = True
            return met_prereqs

        met_prereqs = required_plugins.issubset(enabled_plugins)

        return met_prereqs

    def filters(self):
        return {
            'get_enabled_plugins': self.get_enabled_plugins,
            'get_disables': self.get_disables,
            'get_manifests': self.get_manifests,
            'get_manifest_configs': self.get_manifest_configs,
            'get_manifest_namespaces': self.get_manifest_configs,
            'get_helm_repos': self.get_helm_repos,
            'get_helm_namespaces': self.get_helm_namespaces,
            'get_helm_charts':self.get_helm_charts,
            'validate_prereqs':self.validate_prereqs
        }
    
if __name__ == "__main__":
    #stupid little section i use to debug the filter
    import yaml

    cluster_config = yaml.safe_load(open('./config/cluster-config.yaml'))
    plugin_defs = yaml.safe_load(open('./plugin_map.yaml'))

    filter =  FilterModule()

    print(filter.get_disables(cluster_config,plugin_defs))
    print(filter.get_enabled_plugins(cluster_config,plugin_defs))
    print(filter.get_manifests(cluster_config,plugin_defs))
    print(filter.get_manifest_configs(cluster_config,plugin_defs))
    print(filter.get_helm_repos(cluster_config,plugin_defs))
    print(filter.get_helm_namespaces(cluster_config,plugin_defs))
    print(filter.get_helm_charts(cluster_config,plugin_defs,'/Users/dave/install-k3s'))
    print(filter.validate_prereqs(cluster_config,plugin_defs))