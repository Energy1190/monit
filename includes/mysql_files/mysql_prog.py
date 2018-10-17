#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pymysql
from plumbum import cli
from traceback import format_exc

class MyApp(cli.Application):
    def main(self, *args):
        max_timewait = 0
        max_connection = 0

        try:
            max_tc = '.'.join(os.path.realpath(__file__).split('/')[-1].replace('mysql_prog_','').split('.')[:-1])
            max_connection, max_timewait = max_tc.split('_')
        except:
            print('Error in {}.'.format(os.path.realpath(__file__)))
            print(format_exc())
            sys.exit(1)

        hostname = os.environ.get('MYSQL_HOST')
        username = os.environ.get('MYSQL_USER')
        password = os.environ.get('MYSQL_PASSWORD')
        database = os.environ.get('MYSQL_DATABASE')

        longtime_users = os.environ.get('MYSQL_LONGTIME_USERS')
        if longtime_users:
            longtime_users = longtime_users.split(';')
        else:
            longtime_users = ['root']

        if not all([hostname,username,password,database]):
            print('Failed to get variables.')
            sys.exit(1)

        db = pymysql.connect(hostname,username,password,database)
        cursor = db.cursor()
        cursor.execute("SHOW FULL PROCESSLIST")
        data = cursor.fetchall()

        if len(data) > int(max_connection):
            print('Too many database connections: {}'.format(str(len(data))))
            sys.exit(2)

        timewaits = [(item[5],item[7]) for item in data if int(item[5]) > int(max_timewait) and item[1] not in longtime_users]
        if len(timewaits):
            print('The database receives very long querys.')
            [ print(item) for item in timewaits]
            sys.exit(3)

        sys.exit(0)

if __name__ == "__main__":
    MyApp.run()
