import os
import importlib
from shutil import copyfile
from traceback import format_exc

CONFIG = []         # list names
PROGRAM = []        # list names
DEPEND = {}         # depend dict
SELFDIR = ''        # path

def get_mysql_lib(recursion=0):
    try:
        lib = importlib.import_module('pymysql')
    except:
        print('No library found. Try to install.')
        print(format_exc())

        os.system('pip3 install --upgrade setuptools')
        os.system('pip3 install pymysql')
        recursion += 1
        if recursion > 3:
            print('No library found. Fatal.')
            print(format_exc())
            return None

        lib = get_mysql_lib(recursion)
    return lib

def get_mysql_client(mysql, envs):
    try:
        importlib.reload(mysql)
        client = mysql.connect(envs.get('MYSQL_HOST'),envs.get('MYSQL_USER'),
                               envs.get('MYSQL_PASSWORD'),envs.get('MYSQL_DATABASE'))
    except:
        print('Unable to connect to docker socket.')
        print(format_exc())

        return None
    return client

def build_depend(envs, depend):
    envs.add_env('MYSQL_CHECK', {'default': 'disable', 'requered': False, 'value': None})
    envs.add_env('MYSQL_HOST', {'default': 'localhost', 'requered': False, 'value': None})
    envs.add_env('MYSQL_USER', {'default': 'root', 'requered': False, 'value': None})
    envs.add_env('MYSQL_PASSWORD', {'default': None, 'requered': False, 'value': None})
    envs.add_env('MYSQL_DATABASE', {'default': 'mysql', 'requered': False, 'value': None})
    envs.add_env('MYSQL_MAXCONN', {'default': 200, 'requered': False, 'value': None})
    envs.add_env('MYSQL_MAXTIME', {'default': 360, 'requered': False, 'value': None})
    if envs.get('MYSQL_CHECK') == 'disable': return None

    mysql_lib = get_mysql_lib()
    mysql_client = get_mysql_client(mysql_lib,envs)
    if not mysql_client:
        print('Failed to establish a connection to the database.')
        return None
    else:
        mysql_client.close()

    global CONFIG, PROGRAM
    config = 'mysql_conf'
    path = os.path.join(SELFDIR, 'mysql_conf' + '.tmpl')
    path_new = os.path.join(SELFDIR, config + '.tmpl')
    copyfile(path, path_new)
    CONFIG.append(config)

    prog = 'mysql_prog_{}_{}'.format(str(envs.get('MYSQL_MAXCONN')), str(envs.get('MYSQL_MAXTIME')))
    path = os.path.join(SELFDIR, 'mysql_prog' + '.py')
    path_new = os.path.join(SELFDIR, prog + '.py')
    copyfile(path, path_new)
    PROGRAM.append(prog)

    depend.config[config] = {'envs':  ['ATTEMPTS','FAILURES', 'TIMEOUT'],
                             'parms': {'name': (depend._simple, prog),
                                       'times': (depend.env.get, 'FAILURES'),
                                       'cycles': (depend.env.get, 'ATTEMPTS'),
                                       'slack': (depend.env.get, 'SLACK_URL'),
                                       'timeout': (depend.env.get, 'TIMEOUT')},
                             'callback': (depend._callback, config)}
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