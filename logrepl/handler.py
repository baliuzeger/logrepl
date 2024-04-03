from pathlib import Path
from datetime import datetime
import sys
import readline
import builtins
from pathlib import Path
import asyncio
import time
from contextlib import asynccontextmanager
from io import TextIOWrapper
from dotenv import dotenv_values

nm_config_dir = 'dir'
nm_config_prefix = 'prefix'
nm_config_err_acc_time = 'err_acc_time'
fname_config = '.pylogrepl'
default_dir = '.'

# builtin_read = sys.__stdin__.read
# builtin_readline = sys.__stdin__.readline
builtin_input = builtins.input
# builtin_stdout_write = sys.__stdout__.write
builtin_stderr_write = sys.__stderr__.write

def gen_log_fname(prefix=None):
    t_tag = datetime.now().strftime("%Y%m%d%H%M")
    fname = f"{t_tag}.log"
    if not prefix is None:
        fname = f"{prefix}_{fname}"
    return fname

class LogOutWrapper(TextIOWrapper):
    def __init__(self, ref: TextIOWrapper, decorate):
        super(LogOutWrapper, self).__init__(
            ref.buffer,
            encoding=ref.encoding,
            errors=ref.errors,
            line_buffering=ref.line_buffering,
            write_through=ref.write_through
            # newline use default
        )
        self.write_fn = ref.write
        self.write = decorate(self.write_fn)

class LogInWrapper(TextIOWrapper):
    def __init__(self, ref: TextIOWrapper, decorate):
        super(LogOutWrapper, self).__init__(
            ref.buffer,
            encoding=ref.encoding,
            errors=ref.errors,
            line_buffering=ref.line_buffering,
            write_through=ref.write_through
            # newline use default
        )
        self.read_fn = ref.read
        self.readline_fn = ref.readline
        self.read = decorate(self.read_fn)
        self.readline = decorate(self.readline_fn)

class Handler():

    def __init__(
        self,
        log_dir='.',
        prefix=None,
        err_acc_time=0.5,
        will_log=True,
    ):

        self.log_dir = Path(log_dir)
        self.prefix = prefix
        self.update_suffix()
        self.will_log = will_log

        self.err_acc_time = err_acc_time
        self.last_err_time = None
        self.errors = set()
        self.err_task = None

    @classmethod
    def from_env(
        cls,
        log_dir=None,
        prefix=None,
        err_acc_time=None,
    ):
        config = dotenv_values(fname_config)

        if log_dir is None and nm_config_dir in config:
            log_dir = config[nm_config_dir]

        if prefix is None and nm_config_prefix in config:
            prefix = config[nm_config_prefix]

        if prefix is None and nm_config_err_acc_time in config:
            err_acc_time = config[nm_config_err_acc_time]

        return cls(log_dir, prefix, err_acc_time, True)

    def set_dir(self, log_dir):
        self.log_dir = Path(log_dir)
        self.update_suffix(self)

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.update_suffix()

    def update_suffix(self):
        self.log_file = gen_log_fname(self.prefix)

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
        sys.stdout = LogOutWrapper(sys.__stdout__, self.decorate_log_out)
        sys.stderr = LogOutWrapper(sys.__stderr__, self.decorate_log_out)
        sys.stdin = LogInWrapper(sys.__stdin__, self.decorate_log_in)
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
        self.reset_io()

    def stop_log(self):
        print('logrepl stopped log to file.')
        self.set_will_log(False)

    def start_log(self):
        self.set_will_log(True)
        print('logrepl start log to file.')

    def reset_io():
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sys.stdin = sys.__stdin__
        builtins.input = builtin_input # useless for the running repl!!
    
@asynccontextmanager
async def log_handler(
    log_dir=None,
    prefix=None,
    err_acc_time=None,
    will_log=True,
):
    hd = Handler.from_env(log_dir, prefix, err_acc_time, will_log)
    try:
        yield hd
    finally:
        await hd.exit()