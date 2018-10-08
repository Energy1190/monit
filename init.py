#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
time_start = time.time()

def msg(module,function,message,func, time_start=0):
    time_msg = time.time()
    msg_module = '{}:{}'.format(str(module),str(function))
    if len(msg_module) < 55: msg_module += ' ' * (55 - len(msg_module))

    msg_time = '{}| Time: {} '.format(msg_module, str(round(time_msg - time_start, 3)))
    if len(msg_time) < 70: msg_time += ' ' * (70 - len(msg_time))

    msg_out = '{}| -> {}'.format(msg_time, str(message))
    func(msg_out)

logging.basicConfig(level=logging.DEBUG)

msg(__name__,'init','Begin.', logging.info, time_start=time_start)
msg(__name__,'init:import','Begin.', logging.info, time_start=time_start)

try:
    from shutil import copyfile
    from jinja2 import Environment, FileSystemLoader
except:
    msg(__name__, 'init:import', 'Fail.', logging.error, time_start=time_start)
    sys.exit(1)

msg(__name__, 'init:import', 'Success.', logging.info, time_start=time_start)
msg(__name__, 'init:load', 'Begin.', logging.info, time_start=time_start)

class Env():
    envs = {'MAIL_SERVER': {'default': None, 'requered': True, 'value': None},
                  'MAIL_PORT': {'default': 25, 'requered': True, 'value': None},
                  'MAIL_ADDRESS': {'default': None, 'requered': True, 'value': None},
                  'MAIL_USER': {'default': None, 'requered': True, 'value': None},
                  'MAIL_PASSWORD': {'default': None, 'requered': True, 'value': None},
                  'GENERATE': {'default': 'mailsend;host', 'requered': True, 'value': None},
                  'PROGRAMS': {'default': None, 'requered': False, 'value': None},
                  'SEND_DATA': {'default': None, 'requered': False, 'value': None}}
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

    def get_hostname(self):
        self.host = None
        if os.environ.get('HOST'):
            self.host = os.environ.get('HOST')
        elif os.path.exists('/etc/virthostname'):
            self.host = str(open('/etc/virthostname', 'r').read()).replace('\n', '')
        elif os.path.exists('/host/root/etc/hostname'):
            self.host = str(open('/host/root/etc/hostname', 'r').read()).replace('\n', '')
        elif os.path.exists('/etc/hostname'):
            self.host = str(open('/etc/hostname', 'r').read()).replace('\n', '')

        if self.host:
            msg(__name__, 'env:get_hostname', self.host, logging.info, time_start=time_start)
            if os.name != 'nt' and not os.path.exists('/etc/virthostname'):
                open('/etc/virthostname', 'w').write(self.host)
            else:
                msg(__name__, 'env:get_hostname', 'Not support windows.', logging.error, time_start=time_start)
                sys.exit(1)
        else:
            msg(__name__, 'env:get_hostname', 'Fail', logging.error, time_start=time_start)
            sys.exit(1)

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

def set_generate_files(env_val, envs=None):
    result = {}
    for val in env_val.split(sep=';'):
        result[val] = {}

    for val in result:
        parms = {}
        if val == 'mailsend':
            alert_set = ''.join(['set alert {} only on {}\n'.format(i, '{status, size, resource}')
                                 for i in envs.envs['MAIL_ADDRESS']['value'].split(sep=';')])
            auth_set = '{} {}'.format(envs.envs['MAIL_USER']['value'], envs.envs['MAIL_PASSWORD']['value'])
            parms = {'name': envs.host,
                     'mail': alert_set,
                     'server': envs.envs['MAIL_SERVER']['value'],
                     'port': envs.envs['MAIL_PORT']['value'],
                     'auth': auth_set}
        elif val == 'host':
            parms = {'name': envs.host}

        if val: result[val] = parms

    return result


def set_generate_programs(env_val, envs=None):
    result = {}

    if not env_val: return result
    for val in env_val.split(sep=';'):
        if val: result[val] = {}

    for val in result:
        params = {}
        result[val] = params

    return result

msg(__name__, 'init:load', 'Success.', logging.info, time_start=time_start)

def main():
    msg(__name__, 'main:main', 'Begin.', logging.info, time_start=time_start)
    path_config = '/etc/monit.d/'
    path_template = '/app/templates/'
    path_programs = '/app/programs'

    msg(__name__, 'main:env', 'Begin.', logging.info, time_start=time_start)
    envs = Env()

    msg(__name__, 'main:env', 'Validation.', logging.info, time_start=time_start)
    envs.self_check()

    msg(__name__, 'main:env', 'Saerch host.', logging.info, time_start=time_start)
    envs.get_hostname()

    if not os.path.isfile('/vm_status'):
        msg(__name__, 'main:env', 'Metal bar.', logging.info, time_start=time_start)
        envs.envs['GENERATE']['value'] += ';{}'.format('temp')

    msg(__name__, 'main:env', 'Success.', logging.info, time_start=time_start)
    msg(__name__, 'main:generator', 'Begin.', logging.info, time_start=time_start)

    generate_files = set_generate_files(envs.envs['GENERATE']['value'], envs=envs)
    generate_programs = set_generate_programs(envs.envs['PROGRAMS']['value'], envs=envs)

    msg(__name__, 'main:generator', 'Generation.', logging.info, time_start=time_start)
    Generator(path_template, path_config, path_programs, envs=envs,
              generate_dict=generate_files,
              progarms_dict=generate_programs)

    msg(__name__, 'main:generator', 'Success.', logging.info, time_start=time_start)
    msg(__name__, 'main:main', 'Success.', logging.info, time_start=time_start)

if __name__ == "__main__":
    main()