#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import docker
from plumbum import cli
from traceback import format_exc

class MyApp(cli.Application):
    def main(self, *args):
        try:
            name = '.'.join(os.path.realpath(__file__).split('/')[-1].replace('docker_prog_','').split('.')[:-1])
            client = docker.client.DockerClient(base_url=os.environ.get('DOCKER_SOCKET'))
            container = client.containers.get(name)

            print(name, container.status)
            sys.exit(0)
        except:
            print(format_exc())
            sys.exit(1)

if __name__ == "__main__":
    MyApp.run()