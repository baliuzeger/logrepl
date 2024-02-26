import argparse
import code
from pathlib import Path

import sys
import readline
import builtins
from pathlib import Path

def check_dir_write(log_path, msg):
    log_path = Path(log_path)
    log_path.parent.mkdir(exist_ok=True, parents=True)
    with open(log_path, 'a') as log:
        log.write(msg)

def decorate_log_out(log_path, fn):
    def new_func(*args, **kwargs):
        try:
            check_dir_write(log_path, args[0])
        except Exception as e:
            print(f"logged out error: {e}")
        finally:
           return fn(*args, **kwargs)
    return new_func

def decorate_log_in(log_path, fn):
    def new_func(*args, **kwargs):
        s = fn(*args, **kwargs)
        try:
            check_dir_write(log_path, s)
        except Exception as e:
            print(f"logged read error: {e}")
        finally:
           return s
    return new_func

builtin_input = builtins.input

def gen_logged_input(log_path):

    def logged_input(prompt=''):
        got = builtin_input(prompt)
        try:
            check_dir_write(log_path, f'{prompt}{got}\n')
        except Exception as e:
            print(f"logged input error: {e}")
        finally:
            pass
        return got
    
    return logged_input

def set_path(log_path):
    sys.stdout.write = decorate_log_out(log_path, sys.stdout.write)
    sys.stderr.write = decorate_log_out(log_path, sys.stderr.write)
    sys.stdin.read = decorate_log_in(log_path, sys.stdin.read)
    sys.stdin.readline = decorate_log_in(log_path, sys.stdin.readline)
    builtins.input = gen_logged_input(log_path)

def reset():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    sys.stdin = sys.__stdin__
    builtins.input = builtin_input

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="prefix for log file")
    parser.add_argument('-d', '--dir', default='.', help="dir for log file")
    args = parser.parse_args()

    if args.dir is None:
        # get from .env
        dir_log = Path('.')

    log_path = dir_log/utlog.gen_log_fname(args.prefix)
    set_path(log_path)
    code.interact()



