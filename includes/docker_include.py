import os
import importlib
from shutil import copyfile

CONFIG = []         # list names
PROGRAM = []        # list names
DEPEND = {}         # depend dict
SELFDIR = os.path.join('/'.join(os.path.realpath(__file__).split('/')[:-1]), 'docker')        # path

def get_docker_lib():
    try:
        lib = importlib.import_module('docker')
    except:
        os.system('pip3 install docker')
        lib = get_docker_lib()
    return lib

def get_docker_client(docker, envs):
    try:
        client = docker.DockerClient(base_url=envs.get('DOCKER_SOCKET'))
    except:
        print('Unable to connect to docker socket.')
        return None
    return client

def build_files(name, envs=None, depend=None):
    pass

def detect_docker_containers(envs,depend):
    docker_lib = get_docker_lib()
    docker_client = get_docker_client(docker_lib,envs)
    if not docker_client: return None

    return docker_lib

def build_depend(envs, depend):
    envs.add_env('DOCKER_CONTAINERS', {'default': 'disable', 'requered': False, 'value': None})
    envs.add_env('DOCKER_SOCKET', {'default': '/var/run/docker.sock', 'requered': False, 'value': None})
    if envs.get('DOCKER_CONTAINERS') == 'disable': return None

    docker_lib = None
    if envs.get('DOCKER_CONTAINERS') ==  'auto':
        docker_lib = detect_docker_containers(envs,depend)
    else:
        containers = envs.get('DOCKER_CONTAINERS').split(';')
        [build_files(container,envs,depend) for container in containers if container]

    if not docker_lib:
        os.system('pip3 install docker')

def get(name):
    if name == 'config': return CONFIG
    if name == 'program': return PROGRAM

def callback(temlate_path):
    for item in CONFIG:
        path = os.path.join(SELFDIR,item + '.tmpl')
        path_new = os.path.join(temlate_path,item + '.tmpl')
        if os.path.exists(path): copyfile(path,path_new)

    for item in PROGRAM:
        path = os.path.join(SELFDIR,item + '.py')
        path_new = os.path.join(temlate_path,item + '.py')
        if os.path.exists(path): copyfile(path,path_new)