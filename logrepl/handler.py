from pathlib import Path
from datetime import datetime
import sys
import readline
import builtins
from pathlib import Path
import time
from contextlib import contextmanager
from io import TextIOWrapper
from threading import Thread
from dotenv import dotenv_values
from functools import reduce
from queue import Queue

nm_config_dir = 'dir'
nm_config_prefix = 'prefix'
nm_config_err_acc_time = 'err_acc_time'
fname_config = '.pylogrepl'
default_dir = '.'
default_err_acc_time = 1.
default_will_log = True

is_debug = False

def debug_write(msg):
    if is_debug:
        with open('debug.log', 'a') as log:
            log.write(f'{msg}\n')

# builtin_read = sys.__stdin__.read
# builtin_readline = sys.__stdin__.readline
builtin_input = builtins.input
builtin_stdout_write = sys.__stdout__.write
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
        super(LogInWrapper, self).__init__(
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

def arg_config_default(arg, dict_config, nm_config, default, type_fn):
    if arg is None:
        if nm_config in dict_config:
            return type_fn(dict_config[nm_config])
        else:
            return default
    else:
        return arg

class Handler():

    def __init__(
        self,
        log_dir=default_dir,
        prefix=None,
        err_acc_time=default_err_acc_time,
        will_log=default_will_log,
    ):

        self.log_dir = Path(log_dir)
        self.prefix = prefix
        self.update_suffix()
        self.will_log = will_log

        self.err_acc_time = err_acc_time
        self.last_err_time = None
        self.errors = Queue()
        self.err_thread = None

    @classmethod
    def from_env(
        cls,
        log_dir=None,
        prefix=None,
        err_acc_time=None,
    ):
        config = dotenv_values(fname_config)

        log_dir = arg_config_default(log_dir, config, nm_config_dir, default_dir, str)

        if prefix is None and nm_config_prefix in config:
            prefix = str(config[nm_config_prefix])

        err_acc_time = arg_config_default(
            err_acc_time,
            config,
            nm_config_err_acc_time,
            default_err_acc_time,
            float
        )

        return cls(log_dir, prefix, err_acc_time, True)

    def set_dir(self, log_dir):
        """
        Update new logging dir.
        log_dir must be string or Path.
        The suffix _yyyymmddhhmm.log will also be updated.
        """
        self.log_dir = Path(log_dir)
        self.update_suffix(self)

    def set_prefix(self, prefix):
        """
        Update new prefix for the log file.
        `prefix` sholud be `str` or `None`.
        The suffix `_yyyymmddhhmm.log` will also be updated
        while the `log_dir` will remain unchanged.
        Drop the prefix of new log file by setting `prefix` as `None`.
        """
        self.prefix = prefix
        self.update_suffix()

    def update_suffix(self):
        """
        Update the timestamp suffix with `log_dir` & `prefix` unchanged.
        """
        self.log_file = gen_log_fname(self.prefix)

    def set_will_log(self, log_or_not):
        self.will_log = log_or_not
    
    def get_path(self):
        if self.log_file is None:
            raise ValueError('logrepl log_file is None.')
        return self.log_dir/self.log_file
    
    def check_dir_write(self, msg):
        if self.will_log:
            # raise Exception(f'dead {self.errors.qsize() % 2}') # for debug
            self.log_dir.mkdir(exist_ok=True, parents=True)
            with open(self.get_path(), 'a') as log:
                log.write(msg)

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

    def show_err(self):
        try:
            time_diff = time.time() - self.last_err_time
            while time_diff < self.err_acc_time:
                time.sleep(self.err_acc_time)
                time_diff = time.time() - self.last_err_time
            
            set_errs = set()
            while not self.errors.empty():
                set_errs.add(str(self.errors.get(block=False)))

            builtin_stderr_write(
                reduce(
                    lambda acc, x: acc + f'{x}\n',
                    set_errs,
                    '\nlogrepl got errors (ignore the duplicated ones):\n'
                ) + '>>> '
            )
        
        except Exception as e:
            debug_write(str(e))
            builtin_stderr_write(str(e))

    def add_err(self, err):
        try:
            self.last_err_time = time.time()
            self.errors.put(err)
            if self.err_thread is None or not self.err_thread.is_alive():
                thr = Thread(target=self.show_err)
                thr.start()
                self.err_thread = thr
        except Exception as e:
            debug_write(str(e))
            builtin_stderr_write(str(e))
    
    def exit(self):
        if not self.err_thread is None and not self.err_thread.is_alive():
            self.err_thread.join()
        self.reset_io()

    def stop_log(self):
        print('logrepl stopped log to file.')
        self.set_will_log(False)

    def start_log(self):
        self.set_will_log(True)
        print('logrepl start log to file.')

    @staticmethod
    def reset_io():
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sys.stdin = sys.__stdin__
        builtins.input = builtin_input # useless for the running repl!!
    
@contextmanager
def log_handler(
    log_dir=None,
    prefix=None,
    err_acc_time=None,
):
    hd = Handler.from_env(log_dir, prefix, err_acc_time)
    hd.set_io()
    try:
        yield hd
    finally:
        hd.exit()