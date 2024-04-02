from pathlib import Path
from datetime import datetime
import sys
import readline
import builtins
from pathlib import Path
import asyncio
import time
from contextlib import asynccontextmanager

builtin_read = sys.__stdin__.read
builtin_readline = sys.__stdin__.readline
builtin_input = builtins.input
builtin_stdout_write = sys.__stdout__.write
builtin_stderr_write = sys.__stderr__.write

def gen_log_fname(prefix=None):
    t_tag = datetime.now().strftime("%Y%m%d%H%M")
    fname = f"{t_tag}.log"
    if not prefix is None:
        fname = f"{prefix}_{fname}"
    return fname

class Handler():
    def __init__(
        self,
        log_dir=Path('.'),
        log_file=None,
        will_log=True,
        err_acc_time=0.5
    ):

        self.log_dir = log_dir
        self.log_file = log_file
        self.will_log = will_log

        self.err_acc_time = err_acc_time
        self.last_err_time = None
        self.errors = set()
        self.err_task = None

    def set_dir(self, new_dir, prefix=None):
        self.log_dir = Path(new_dir)
        self.log_file = gen_log_fname(prefix)

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
                # breakpoint()
                raise Exception('dead!!!!')

    async def show_err(self):

        while time.time() - self.last_err_time < self.err_acc_time:
            await asyncio.sleep(self.err_acc_time)

        for err in self.errors:
            builtin_stderr_write(err)

        self.errors = set()

    def add_err(self, err):

        self.last_err_time = time.time()
        self.errors.add(err)

        if self.err_task is None or self.err_task.done():
            self.err_task = asyncio.create_task(self.show_err())
    
    async def exit(self):
        if not self.err_task is None and not self.err_task.done():
            await self.err_task

def decorate_log_out(fn):
    def new_func(*args, **kwargs):
        try:
            handler.check_dir_write(args[0])
        except Exception as e:
            builtin_stderr_write(f"logrepl got error <{e}> when writing output msg <{args[0]}>.\n")
        finally:
            return fn(*args, **kwargs)
    return new_func

def decorate_log_in(fn):
    def new_func(*args, **kwargs):
        s = fn(*args, **kwargs)
        try:
            handler.check_dir_write(s)
        except Exception as e:
            builtin_stderr_write(f"logrepl got error <{e}> when writting stdin msg <{s}>.\n")
        finally:
            return s
    return new_func

def logged_input(prompt=''):
    got = builtin_input(prompt)
    try:
        handler.check_dir_write(f'{prompt}{got}\n')
    except Exception as e:
        builtin_stderr_write(f"logrepl got error <{e}> when writting input msg <{prompt}{got}>.\n")
    finally:
        return got

def set_io():
    sys.stdout.write = decorate_log_out(builtin_stdout_write)
    sys.stderr.write = decorate_log_out(builtin_stderr_write)
    sys.stdin.read = decorate_log_in(builtin_read)
    sys.stdin.readline = decorate_log_in(builtin_readline)
    builtins.input = logged_input

def update(prefix=None, new_dir=None):
    if not new_dir is None:
        handler.set_dir(new_dir)
    handler.set_fname(prefix)

def stop_log():
    print('logrepl stopped log to file.')
    handler.set_will_log(False)

def start_log():
    handler.set_will_log(True)
    print('logrepl start log to file.')

def reset_io():
    sys.stdout.write = builtin_stdout_write
    sys.stderr.write = builtin_stderr_write
    sys.stdin.read = builtin_read
    sys.stdin.readline = builtin_readline
    builtins.input = builtin_input # useless for the running repl!!