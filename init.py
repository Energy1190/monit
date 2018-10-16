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
    import importlib
    from shutil import copyfile
    from traceback import format_exc
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
                                             'slack': (self.env.get, 'SLACK_URL'),
                                             'auth': (self._build_auth, 'MAIL_USER','MAIL_PASSWORD')},
                                   'callback': (self._callback, 'mailsend')},
                       'host':    {'envs':  ['HOSTNAME', 'ATTEMPTS', 'MAX_CPU', 'MAX_RAM', 'MAX_LOAD'],
                                   'parms': {'name': (self.env.get, 'HOSTNAME'),
                                             'cpu': (self.env.get, 'MAX_CPU'),
                                             'ram': (self.env.get, 'MAX_RAM'),
                                             'load': (self.env.get, 'MAX_LOAD'),
                                             'slack': (self.env.get, 'SLACK_URL'),
                                             'cycles': (self.env.get, 'ATTEMPTS')},
                                   'callback': (self._callback, 'host')},
                       'temp':    {'envs':  ['ATTEMPTS','FAILURES'],
                                   'parms': {'times': (self.env.get, 'FAILURES'),
                                             'slack': (self.env.get, 'SLACK_URL'),
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
                                             'slack': (self.env.get, 'SLACK_URL'),
                                             'cycles': (self.env.get, 'ATTEMPTS')},
                                   'callback': (self._callback, 'fs')},
                       'default':  {'envs':  ['REPEAT'],
                                    'parms': {'daemon': (self.env.get, 'REPEAT')},
                                    'callback': (self._callback, 'default')}}

    def _simple(self, name):
        return name

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
                    'REPEAT': {'default': 120, 'requered': False, 'value': None},
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
                    'FILESYSTEMS': {'default': 'auto', 'requered': False, 'value': None},
                    'ENV_FILE': {'default': './.env', 'requered': False, 'value': None},
                    'TIMEOUT': {'default': 120, 'requered': False, 'value': None},
                    'SLACK_URL': {'default': None, 'requered': False, 'value': None}}

    prog_pattern = 'ADD_PROG_'
    conf_pattern = 'ADD_CONF_'
    def self_check(self):
        self._init()

        self._rff(self.get('ENV_FILE'))
        self._init()

        self._add()

    def _init(self):
        for env in self.envs:
            if os.environ.get(env):
                self.envs[env]['value'] = os.environ.get(env)

        for env in self.envs:
            if not self.envs[env]['value'] and self.envs[env]['default']:
                self.envs[env]['value'] = self.envs[env]['default']

        for env in self.envs:
            if not self.envs[env]['value'] and self.envs[env]['requered']:
                msg(__name__, 'env:validate', 'Fail. {}.'.format(env), logging.error, time_start=time_start)
                sys.exit(1)

    def _add(self):
        for env in os.environ:
            if self.prog_pattern in env: self.add_item('PROGRAMS',os.environ[env])
            if self.conf_pattern in env: self.add_item('GENERATE',os.environ[env])

    def add_item(self, item, obj):
        if self.envs[item].get('value'):
            self.envs[item]['value'] += ';{}'.format(obj)
        else:
            self.envs[item]['value'] = ';{}'.format(obj)

    def add_env(self, name, val_dict):
        self.envs[name] = val_dict
        for env in os.environ:
            if env == name: self.envs[name]['value'] = os.environ[env]

        if not self.envs[name]['value'] and self.envs[name]['default']:
            self.envs[name]['value'] = self.envs[name]['default']

    def _rpg(self, name):
        # Random password generate
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
        file = open('.{}_pass'.format(name), 'w')
        file.write(password)
        file.close()

        return password

    def _rff(self, path):
        # Read from file
        if os.path.exists(path):
            with open(path) as read_env:
                for raw_env in read_env:
                    try:
                        name, data = raw_env.split('=')
                        if name in self.envs: self.envs[name]['value'] = data.replace('\n','').replace('\r','')
                    except:
                        pass

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

        self._check_path()
        self.generate_files = generate_dict
        self.generate_progams = progarms_dict

        if self.generate_files:
            for obj in self.generate_files:
                if not obj: continue
                self.generate_file_from_tmpl('{}{}.conf'.format(self.target_dir, obj),
                                             '{}.tmpl'.format(obj),
                                             **self.generate_files[obj])

        if self.generate_progams:
            for obj in self.generate_progams:
                if not obj: continue
                self.generate_programs_from_tmpl('{}/{}.py'.format(self.program_dir, obj),
                                                 '{}/{}.py'.format(self.path, obj))

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

def get_includes(path='./includes', templates=None, depend=None, envs=None):
    if not os.path.exists(path): return None
    if not os.path.isdir(path): return None
    if not depend: return None
    if not envs: return None

    sys.path.append(path)
    for item in os.listdir(path):
        sub_path = os.path.join(path,item)
        if os.path.isfile(sub_path) and sub_path.split('.')[-1] == 'py':
            try:
                if '_include' in item:
                    module = item.split('.')[0]
                    lib = importlib.import_module(module)
                    lib.build_depend(envs, depend)

                    config = lib.get('config')
                    if config:
                        [envs.add_item('GENERATE', sub_item) for sub_item in config]

                    program = lib.get('program')
                    if program:
                        [envs.add_item('PROGRAMS', sub_item) for sub_item in program]

                    lib.callback(templates)
                    msg(__name__, 'includes:import', 'Add. {}'.format(item), logging.info, time_start=time_start)
            except:
                msg(__name__, 'includes:import', 'Fail. {}'.format(item), logging.error, time_start=time_start)
                msg(__name__, 'includes:import', 'Traceback {}'.format(str(format_exc())), logging.error, time_start=time_start)

def generate_params(env_val, depend=None):
    if not env_val: return {}

    result = {}
    for val in env_val.split(sep=';'):
        result[val] = {}

    for val in result:
        parms = depend.check(val)
        if val: result[val] = parms

    return result

msg(__name__, 'init:load', 'Success.', logging.info, time_start=time_start)

def main(path_config='/etc/monit.d/', path_template='/templates/', path_programs='/programs', path_includes='./includes'):
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
    msg(__name__, 'main:includes', 'Begin.', logging.info, time_start=time_start)
    get_includes(path_includes,templates=path_template,depend=depend,envs=envs)

    msg(__name__, 'main:includes', 'Success.', logging.info, time_start=time_start)
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
    parser.add_argument('--includes', default='./includes')

    args = parser.parse_args()
    main(args.config,args.templates,args.programs,args.includes)