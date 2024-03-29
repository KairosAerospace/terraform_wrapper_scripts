#!/usr/env/bin/ python3

import os
import psutil
import subprocess
from time import sleep
from contextlib import contextmanager
from .layers import GcpInfra, AwsInfra, Astronomer, SystemComponents
from .utils import git_root

class ConventionError(Exception):
    pass

class AstronomerDeployment():

    VARSFILE_CONVENTION = {
        'google': GcpInfra,
        'aws': AwsInfra
    }

    def __init__(self, varsfile_path, state_path):
        ''' Determine the platform based on
        pathing convention

        environments/
            google/
            aws/
            ... (anything else in VARSFILE_CONVENTION)
        '''
        self._validate_varsfile_path(varsfile_path)

        # the state file needs to either exist or
        # the directory to it exists
        state_path = os.path.realpath(state_path)
        if not (os.path.isfile(state_path) or \
                os.path.isdir(os.path.dirname(state_path))):
            raise FileNotFoundError(state_path)

        self.statefile = os.path.realpath(state_path)
        self.varsfile = os.path.realpath(varsfile_path)

        terraform_directory = os.path.join(git_root(),"terraform")
        self._infra = \
            self.VARSFILE_CONVENTION[self._platform](
                self.varsfile,
                self.statefile,
                terraform_directory)
        self._system_components = SystemComponents(
            self.varsfile,
            self.statefile,
            terraform_directory)
        self._astronomer = Astronomer(
            self.varsfile,
            self.statefile,
            terraform_directory)

    @property
    def proxy(self):
        return "http://127.0.0.1:1234"

    def deploy(self):
        ''' Apply both the infrastructure and
        Astronomer terraform modules.
        '''
        # apply the infrastructure layer
        self._infra.apply()

        https_proxy = self.proxy

        # TODO: avoid collisions on helm home and kubeconfig
        environment = {
            "https_proxy": https_proxy,
            "http_proxy": https_proxy,
            "HTTPS_PROXY": https_proxy,
            "HTTP_PROXY": https_proxy,
            "HELM_HOME": os.path.realpath(
                os.path.join(git_root(),".helm")),
            "KUBECONFIG": os.path.realpath(
                os.path.join(git_root(),
                             "terraform",
                             "kubeconfig"))
        }
        # enabling a proxy through the bastion host,
        # apply the astronomer layer
        with self._proxy_on() as process:
            # Give some time for the proxy command
            # to establish the connection,
            sleep(10)
            # then run terraform through the proxy
            self._system_components.apply(
                environment=environment)
                # refresh=False)
            # then run terraform through the proxy
            self._astronomer.apply(
                environment=environment)
                # refresh=False)

    @property
    def _platform(self):
        ''' Return the platform label, based on
        the variables path convention.
        '''
        directory_path = os.path.dirname(self.varsfile)
        directory_name = os.path.basename(directory_path)
        return directory_name

    @contextmanager
    def _proxy_on(self):
        command = self._infra._proxy_command()
        with self._background_process(command) as process:
            yield process

    @contextmanager
    def _background_process(self, command):
        ''' Context management for running
        background processes that we wish
        to ensure are cleaned up.
        '''
        process = subprocess.Popen(
                command,
                shell=True)
        try:
            yield process
        finally:
            self._kill_process(process.pid)

    def _kill_process(self, proc_pid):
        ''' Kill a process and all
        child processes
        '''
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    def _validate_varsfile_path(self, path):
        ''' Throw informative error message
        when convention is violated.
        '''
        if not os.path.isfile(path):
            raise FileNotFoundError(path)

        full_path = os.path.realpath(path)
        directory_path = os.path.dirname(path)
        directory_name = os.path.basename(directory_path)
        if directory_name not in self.VARSFILE_CONVENTION:
            raise ConventionError(
                "The vars file should be placed in a " + \
                "directory with one of the following " + \
                f"names: {self.VARSFILE_CONVENTION.keys()}")

