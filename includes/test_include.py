import os
from shutil import copyfile

CONFIG = ['test_conf']         # list names
PROGRAM = ['test_prog.py']        # list names
DEPEND = {}                    # depend dict
SELFDIR = os.path.join(os.path.realpath(__file__), 'test')        # path


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
        path = os.path.join(SELFDIR,item)
        path_new = os.path.join(temlate_path,item)
        if os.path.exists(path): copyfile(path,path_new)