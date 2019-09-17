import getpass, inspect
import os

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) 

def user_config_dir(programm,company):
    """quick and dirty fix for C:User getting deleted in school"""
    username = getpass.getuser()
    return os.path.abspath(os.path.join(PATH,"..","..","..","..","config",username))
