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
        prefix=None,
        log_dir=Path('.'),
        err_acc_time=0.5,
        will_log=True,
    ):

        self.set_dir(log_dir, prefix)
        self.will_log = will_log

        self.err_acc_time = err_acc_time
        self.last_err_time = None
        self.errors = set()
        self.err_task = None

    def set_dir(self, log_dir, prefix=None):
        self.log_dir = Path(log_dir)
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
                # raise Exception('dead!!!!')

    def decorate_log_out(self, fn):
        def new_func(*args, **kwargs):
            try:
                self.check_dir_write(args[0])
            except Exception as e:
                self.add_err(str(e))
            finally:
                return fn(*args, **kwargs)
        return new_func

    def decorate_log_in(self, fn):
        def new_func(*args, **kwargs):
            s = fn(*args, **kwargs)
            try:
                self.check_dir_write(s)
            except Exception as e:
                self.add_err(str(e))
            finally:
                return s
        return new_func

    def gen_logged_input(self):

        def logged_input(prompt=''):
            got = builtin_input(prompt)
            try:
                self.check_dir_write(f'{prompt}{got}\n')
            except Exception as e:
                self.add_err(str(e))
            finally:
                return got
        
        return logged_input

    def set_io(self):
        sys.stdout.write = self.decorate_log_out(builtin_stdout_write)
        sys.stderr.write = self.decorate_log_out(builtin_stderr_write)
        sys.stdin.read = self.decorate_log_in(builtin_read)
        sys.stdin.readline = self.decorate_log_in(builtin_readline)
        builtins.input = self.gen_logged_input()

    async def show_err(self):

        while time.time() - self.last_err_time < self.err_acc_time:
            await asyncio.sleep(self.err_acc_time)

        builtin_stderr_write('logrepl got errors (ignore the duplicated ones):\n')

        for err in self.errors:
            builtin_stderr_write(f'{err}\n')

        self.errors = set()

    def add_err(self, err):

        self.last_err_time = time.time()
        self.errors.add(err)

        if self.err_task is None or self.err_task.done():
            self.err_task = asyncio.create_task(self.show_err())
    
    async def exit(self):
        if not self.err_task is None and not self.err_task.done():
            await self.err_task

    def stop_log(self):
        print('logrepl stopped log to file.')
        self.set_will_log(False)

    def start_log(self):
        self.set_will_log(True)
        print('logrepl start log to file.')

    def reset_io():
        sys.stdout.write = builtin_stdout_write
        sys.stderr.write = builtin_stderr_write
        sys.stdin.read = builtin_read
        sys.stdin.readline = builtin_readline
        builtins.input = builtin_input # useless for the running repl!!
    
@asynccontextmanager
async def log_handler(
    prefix=None,
    log_dir=Path('.'),
    err_acc_time=0.5,
    will_log=True,
):
    hd = Handler(prefix, log_dir, err_acc_time, will_log)
    try:
        yield hd
    finally:
        await hd.exit()