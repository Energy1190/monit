#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from plumbum import cli

class MyApp(cli.Application):
    def main(self, *args):
        print("Hello, it's test.")
        sys.exit(0)

if __name__ == "__main__":
    MyApp.run()