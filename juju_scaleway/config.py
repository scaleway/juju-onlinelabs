# -*- coding: utf-8 -*-
#
# Copyright (c) 2014-2015 Online SAS and Contributors. All Rights Reserved.
#                         Edouard Bonlieu <ebonlieu@scaleway.com>
#                         Julien Castets <jcastets@scaleway.com>
#                         Manfred Touron <mtouron@scaleway.com>
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause

import os
import yaml
import sys

from juju_scaleway.env import Environment
from juju_scaleway.exceptions import ConfigError
from juju_scaleway import provider


class Config(object):

    def __init__(self, options):
        self.options = options

    def connect_provider(self):
        """Connect to Scaleway.
        """
        return provider.factory()

    def connect_environment(self):
        """Return a websocket connection to the environment.
        """
        return Environment(self)

    def validate(self):
        provider.validate()
        self.get_env_name()

    @property
    def verbose(self):
        return self.options.verbose

    @property
    def constraints(self):
        return self.options.constraints

    @property
    def series(self):
        return self.options.series

    @property
    def upload_tools(self):
        return getattr(self.options, 'upload_tools', False)

    @property
    def num_machines(self):
        return getattr(self.options, 'num_machines', 0)

    @property
    def juju_home(self):
        jhome = os.environ.get("JUJU_HOME")
        if jhome is not None:
            return os.path.expanduser(jhome)
        if sys.platform == "win32":
            return os.path.join(
                os.path.join('APPDATA'), "Juju")
        return os.path.expanduser("~/.juju")

    def get_env_name(self):
        """Get the environment name.
        """
        if self.options.environment:
            return self.options.environment
        elif os.environ.get("JUJU_ENV"):
            return os.environ['JUJU_ENV']

        env_ptr = os.path.join(self.juju_home, "current-environment")
        if os.path.exists(env_ptr):
            with open(env_ptr) as handle:
                return handle.read().strip()

        with open(self.get_env_conf()) as handle:
            conf = yaml.safe_load(handle.read())
            if 'default' not in conf:
                raise ConfigError("No Environment specified")
            return conf['default']

    def get_env_conf(self):
        """Get the environment config file.
        """
        conf = os.path.join(self.juju_home, 'environments.yaml')
        if not os.path.exists(conf):
            raise ConfigError("Juju environments.yaml not found %s" % conf)
        return conf
