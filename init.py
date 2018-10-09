#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import random
import string
import logging
time_start = time.time()

def msg(module,function,message,func, time_start=0):
    # Logging, according to the time from the beginning of the program.
    time_msg = time.time()
    msg_module = '{}:{}'.format(str(module),str(function))
    if len(msg_module) < 55: msg_module += ' ' * (55 - len(msg_module))

    msg_time = '{}| Time: {} '.format(msg_module, str(round(time_msg - time_start, 3)))
    if len(msg_time) < 70: msg_time += ' ' * (70 - len(msg_time))

    msg_out = '{}| -> {}'.format(msg_time, str(message))
    func(msg_out)

def auto_detect_filesystems():
    # Only ext4 file system
    if 'linux' not in sys.platform: return {}
    path = '/proc/fs/ext4/'
    return {device: '/dev/{}'.format(device) for device in os.listdir(path)}


logging.basicConfig(level=logging.DEBUG)

msg(__name__,'init','Begin.', logging.info, time_start=time_start)
msg(__name__,'init:import','Begin.', logging.info, time_start=time_start)

try:
    import argparse
    from shutil import copyfile
    from jinja2 import Environment, FileSystemLoader
except:
    msg(__name__, 'init:import', 'Fail.', logging.error, time_start=time_start)
    sys.exit(1)

msg(__name__, 'init:import', 'Success.', logging.info, time_start=time_start)
msg(__name__, 'init:load', 'Begin.', logging.info, time_start=time_start)

class TemplateDepend():
    def __init__(self, envs=None):
        self.env = envs
        self.config = {'mailsend':{'envs':  ['MAIL_ADDRESS', 'MAIL_USER', 'MAIL_PASSWORD', 'MAIL_SERVER', 'HOSTNAME'],
                                   'parms': {'name': (self.env.get, 'HOSTNAME'),
                                             'mail': (self._build_alert, 'MAIL_ADDRESS'),
                                             'server': (self.env.get, 'MAIL_SERVER'),
                                             'port': (self.env.get, 'MAIL_PORT'),
                                             'auth': (self._build_auth, 'MAIL_USER','MAIL_PASSWORD')},
                                   'callback': (self._callback, 'mailsend')},
                       'host':    {'envs':  ['HOSTNAME', 'ATTEMPTS', 'MAX_CPU', 'MAX_RAM', 'MAX_LOAD'],
                                   'parms': {'name': (self.env.get, 'HOSTNAME'),
                                             'cpu': (self.env.get, 'MAX_CPU'),
                                             'ram': (self.env.get, 'MAX_RAM'),
                                             'load': (self.env.get, 'MAX_LOAD'),
                                             'cycles': (self.env.get, 'ATTEMPTS')},
                                   'callback': (self._callback, 'host')},
                       'temp':    {'envs':  ['ATTEMPTS','FAILURES'],
                                   'parms': {'times': (self.env.get, 'FAILURES'),
                                             'cycles': (self.env.get, 'ATTEMPTS')},
                                   'callback': (self._callback, 'temp')},
                       'httpd':   {'envs':  ['SERVER_PORT','ALLOW_NETWORK', 'ADMIN_PASS', 'USER_PASS'],
                                   'parms': {'port': (self.env.get, 'SERVER_PORT'),
                                             'net': (self.env.get, 'ALLOW_NETWORK'),
                                             'admin_pass': (self.env.get, 'ADMIN_PASS'),
                                             'user_pass': (self.env.get, 'USER_PASS')},
                                   'callback': (self._callback, 'httpd')},
                       'fs':      {'envs':  ['ATTEMPTS','FAILURES','MAX_SPACE','FILESYSTEMS'],
                                   'parms': {'fses': (self._build_fses, 'FILESYSTEMS'),
                                             'hdd': (self.env.get, 'MAX_SPACE'),
                                             'times': (self.env.get, 'FAILURES'),
                                             'cycles': (self.env.get, 'ATTEMPTS')},
                                   'callback': (self._callback, 'fs')},
                       'default':  {'envs':  ['REPEAT'],
                                    'parms': {'daemon': (self._build_fses, 'REPEAT')},
                                    'callback': (self._callback, 'default')}}

    def _build_fses(self, args1):
        result = {}
        incoming = self.env.get(args1)
        if incoming == 'auto':
            result = auto_detect_filesystems()
        else:
            try:
                result = {fs.split('|')[0]:fs.split('|')[1] for fs in incoming.split(';')}
            except:
                msg(__name__, 'depend:build:filesystems', 'Fail. Invalid incoming value.', logging.error, time_start=time_start)
                sys.exit(1)
        return result

    def _build_auth(self, args1, args2):
        return '{} {}'.format(self.env.get(args1), self.env.get(args2))

    def _build_alert(self, args1):
        return ''.join(['set alert {} only on {}\n'.format(i, '{status, size, resource}')
                     for i in self.env.get(args1).split(sep=';')])

    def _callback(self, name):
        for env in self.config[name]['envs']:
            if not self.env.get(env):
                msg(__name__, 'depend:validate', 'Fail. {}'.format(env), logging.error, time_start=time_start)
                sys.exit(1)

        for parm in self.config[name]['parms']:
            func, *args = self.config[name]['parms'][parm]
            self.config[name]['parms'][parm] = func(*args)

        return self.config[name]['parms']

    def check(self, name):
        if self.config.get(name):
            func, *args = self.config[name]['callback']
            return func(*args)
        else:
            return {}


class Env():
    # Information on all possible variables
    def __init__(self):
        self.envs = {'MAIL_SERVER': {'default': None, 'requered': False, 'value': None},
                    'MAIL_PORT': {'default': 25, 'requered': False, 'value': None},
                    'MAIL_ADDRESS': {'default': None, 'requered': False, 'value': None},
                    'MAIL_USER': {'default': None, 'requered': False, 'value': None},
                    'MAIL_PASSWORD': {'default': None, 'requered': False, 'value': None},
                    'GENERATE': {'default': 'mailsend;host', 'requered': False, 'value': None},
                    'PROGRAMS': {'default': None, 'requered': False, 'value': None},
                    'SEND_DATA': {'default': None, 'requered': False, 'value': None},
                    'HOSTNAME': {'default': None, 'requered': False, 'value': None},
                    'ATTEMPTS': {'default': 5, 'requered': False, 'value': None},
                    'FAILURES': {'default': 3, 'requered': False, 'value': None},
                    'MAX_CPU': {'default': '95%', 'requered': False, 'value': None},
                    'MAX_RAM': {'default': '95%', 'requered': False, 'value': None},
                    'MAX_SPACE': {'default': '95%', 'requered': False, 'value': None},
                    'MAX_LOAD': {'default': 4, 'requered': False, 'value': None},
                    'SERVER_PORT': {'default': 2812, 'requered': False, 'value': None},
                    'ALLOW_NETWORK': {'default': "0.0.0.0/0", 'requered': False, 'value': None},
                    'ADMIN_PASS': {'default': self._rpg('admin'), 'requered': False, 'value': None},
                    'USER_PASS': {'default': self._rpg('user'), 'requered': False, 'value': None},
                    'FILESYSTEMS': {'default': 'auto', 'requered': False, 'value': None}}

    prog_pattern = 'ADD_PROG_'
    conf_pattern = 'ADD_CONF_'
    def self_check(self):
        for env in self.envs:
            if os.environ.get(env):
                self.envs[env]['value'] = os.environ.get(env)

        for env in self.envs:
            if not self.envs[env]['value'] and self.envs[env]['default']:
                self.envs[env]['value'] = self.envs[env]['default']

        for env in self.envs:
            if not self.envs[env]['value'] and self.envs[env]['requered']:
                msg(__name__,'env:validate', 'Fail. {}.'.format(env), logging.error, time_start=time_start)
                sys.exit(1)

        for env in os.environ:
            if self.prog_pattern in env: self.envs['PROGRAMS'] += ';{}'.format(os.environ[env])
            if self.conf_pattern in env: self.envs['GENERATE'] += ';{}'.format(os.environ[env])

    def _rpg(self, name):
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
        file = open('.{}_pass'.format(name), 'w')
        file.write(password)
        file.close()

        return password

    def get(self,key):
        return self.envs[key]['value']

    def __getitem__(self, key):
        return self.envs[key]['value']

class Generator():
    def __init__(self, path, tgt, tgt2, generate_dict=None, progarms_dict=None, envs=None):
        self.path = path

        self.envs = envs
        self.target_dir = tgt
        self.program_dir = tgt2

        self.generate_files = generate_dict
        self.generate_progams = progarms_dict
        for obj in self.generate_files:
            self.generate_file_from_tmpl('{}{}.conf'.format(self.target_dir, obj),
                                         '{}.tmpl'.format(obj),
                                         **self.generate_files[obj])

        for obj in self.generate_progams:
            self.generate_programs_from_tmpl('{}/{}.py'.format(self.program_dir, obj),
                                             '{}{}.py'.format(self.path, obj))

    def _check_path(self):
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)

        if not os.path.exists(self.program_dir):
            os.mkdir(self.program_dir)

    def generate_file_from_tmpl(self, path, tmpl, **kwargs):
        try:
            file = open(path, 'w')
            file.writelines(Environment(loader=FileSystemLoader(self.path)).get_template(tmpl).render(kwargs))
            file.close()
        except:
            msg(__name__, 'generator:generate_file:{}'.format(path), 'Fail.', logging.error, time_start=time_start)
            sys.exit(1)

        msg(__name__, 'generator:generate_file:{}'.format(path), 'Success.', logging.info, time_start=time_start)

    def generate_programs_from_tmpl(self, path, tmpl, **kwargs):
        try:
            file = open(path, 'w')
            file.close()

            copyfile(tmpl, path)
            os.chmod(path, 111)
        except:
            msg(__name__, 'generator:generate_program:{}'.format(path), 'Fail.', logging.error, time_start=time_start)
            sys.exit(1)

        msg(__name__, 'generator:generate_program:{}'.format(path), 'Success.', logging.info, time_start=time_start)

def generate_params(env_val, depend=None):
    result = {}
    for val in env_val.split(sep=';'):
        result[val] = {}

    for val in result:
        parms = depend.check(val)
        if val: result[val] = parms

    return result

msg(__name__, 'init:load', 'Success.', logging.info, time_start=time_start)

def main(path_config='/etc/monit.d/', path_template='/templates/', path_programs='/programs'):
    msg(__name__, 'main:main', 'Begin.', logging.info, time_start=time_start)
    msg(__name__, 'main:env', 'Begin.', logging.info, time_start=time_start)
    envs = Env()

    msg(__name__, 'main:env', 'Validation.', logging.info, time_start=time_start)
    envs.self_check()

    if not os.path.isfile('/vm_status'):
        msg(__name__, 'main:env', 'Metal bar.', logging.info, time_start=time_start)
        envs.envs['GENERATE']['value'] += ';{}'.format('temp')

    msg(__name__, 'main:env', 'Success.', logging.info, time_start=time_start)
    msg(__name__, 'main:depend', 'Begin.', logging.info, time_start=time_start)
    depend = TemplateDepend(envs=envs)

    msg(__name__, 'main:depend', 'Success.', logging.info, time_start=time_start)
    msg(__name__, 'main:generator', 'Begin.', logging.info, time_start=time_start)

    generate_files = generate_params(envs.get('GENERATE'), depend=depend)
    generate_programs = generate_params(envs.get('PROGRAMS'), depend=depend)

    msg(__name__, 'main:generator', 'Generation.', logging.info, time_start=time_start)
    Generator(path_template, path_config, path_programs, envs=envs,
              generate_dict=generate_files,
              progarms_dict=generate_programs)

    msg(__name__, 'main:generator', 'Success.', logging.info, time_start=time_start)
    msg(__name__, 'main:main', 'Success.', logging.info, time_start=time_start)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='/etc/monit.d/')
    parser.add_argument('--templates', default='/templates/')
    parser.add_argument('--programs', default='/programs')

    args = parser.parse_args()
    main(args.config,args.templates,args.programs)