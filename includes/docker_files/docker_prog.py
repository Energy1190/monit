#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import docker
from plumbum import cli
from traceback import format_exc

class MyApp(cli.Application):
    def main(self, *args):
        name = None
        container = None

        try:
            name = '.'.join(os.path.realpath(__file__).split('/')[-1].replace('docker_prog_','').split('.')[:-1])
            client = docker.client.DockerClient(base_url=os.environ.get('DOCKER_SOCKET'))
            container = client.containers.get(name)
        except:
            print('Error in {}.'.format(os.path.realpath(__file__)))
            print(format_exc())
            sys.exit(1)

        if container and container.status == 'running':
            sys.exit(0)
        elif container and container.status != 'running':
            print('Container {} is not running, but has status {}'.format(name, container.status))
            sys.exit(1)
        else:
            print('Something went wrong in {}.'.format(os.path.realpath(__file__)))
            sys.exit(1)

if __name__ == "__main__":
    MyApp.run()