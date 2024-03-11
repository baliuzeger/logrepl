import argparse
import code
from pathlib import Path
from datetime import datetime
import sys
import readline
import builtins
from pathlib import Path

def gen_log_fname(prefix=None):
    t_tag = datetime.now().strftime("%Y%m%d%H%M")
    fname = f"{t_tag}.log"
    if not prefix is None:
        fname = f"{prefix}_{fname}"
    return fname

class Config():
    def __init__(self):
        self.log_dir = Path('.')
        self.log_file = None
        self.will_log = False

    def set_dir(self, new_dir):
        self.log_dir = Path(new_dir)

    def set_fname(self, prefix=None):
        self.log_file = gen_log_fname(prefix)

    def set_will_log(self, log_or_not):
        self.will_log = log_or_not
    
    def get_path(self):
            if self.log_file is None:
                raise ValueError('logrepl log_file is None.')
            return self.log_dir/self.log_file
    
    def check_dir_write(self, msg):
        if self.will_log:
            self.log_dir.mkdir(exist_ok=True, parents=True)
            with open(self.get_path(), 'a') as log:
                log.write(msg)

cfg = Config()

def decorate_log_out(fn):
    def new_func(*args, **kwargs):
        try:
            cfg.check_dir_write(args[0])
        except Exception as e:
            sys.__stderr__.write(f"logrepl output error: {e}")
        finally:
           return fn(*args, **kwargs)
    return new_func

def decorate_log_in(fn):
    def new_func(*args, **kwargs):
        s = fn(*args, **kwargs)
        try:
            cfg.check_dir_write(s)
        except Exception as e:
            sys.__stderr__.write(f"logrepl read error: {e}")
        finally:
           return s
    return new_func

builtin_input = builtins.input

def gen_logged_input():

    def logged_input(prompt=''):
        got = builtin_input(prompt)
        try:
            cfg.check_dir_write(f'{prompt}{got}\n')
        except Exception as e:
            sys.__stderr__.write(f"logrepl input error: {e}")
        finally:
            return got

    print(cfg.will_log)
    
    return logged_input

def set_io():
    sys.stdout.write = decorate_log_out(sys.__stdout__.write)
    sys.stderr.write = decorate_log_out(sys.__stderr__.write)
    sys.stdin.read = decorate_log_in(sys.__stdin__.read)
    sys.stdin.readline = decorate_log_in(sys.__stdin__.readline)
    builtins.input = gen_logged_input()

def update(new_dir=None, prefix=None):
    if not new_dir is None:
        cfg.set_dir(new_dir)
    cfg.set_fname(prefix)
    set_io()

def reset_io():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    sys.stdin = sys.__stdin__
    builtins.input = builtin_input # useless for the running repl!!

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="prefix for log file")
    parser.add_argument('-d', '--dir', default='.', help="dir for log file")
    args = parser.parse_args()

    if args.dir is None:
        # get from .env
        pass
    else:
        cfg.set_dir(args.dir)

    cfg.set_fname(args.prefix)
    cfg.set_will_log(True)

    set_io()

    code.interact()

