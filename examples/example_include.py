import os
from shutil import copyfile

CONFIG = []         # list names
PROGRAM = []        # list names
DEPEND = {}         # depend dict
SELFDIR = ''        # path

def build_depend(envs, depend):
    # dependencies are set here
    pass

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