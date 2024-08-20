# Usage
Install:
```
pip install logrepl
```

run the repl:
```
pylogrepl
```

then the whole repl will be logged to the file `yyyymmddhhmm.log`.

You can also use `logrepl` to log the whole stream io of a program by:

```python
import logrepl
with logrepl.log_handler(
    log_dir,
    prefix,
    err_acc_time # usually non-necessary
) as logrepl_handler:
    # import modules and packages
    # run your program here
    # ...
```

Beware that you have to import all the modules and packages in the `with` clause. If a logger of some module or package is initialized before the `with` clause, `logrepl` cannot modify its `logging.StreamHandler`, then all the iniformation directed to that `StreamHandler` will not be logged.

# Config

## Prefix of the log file

use the optional positional argument, for example:
```
pylogrepl prefix
```

then the log file will be `prefix_yyyymmddhhmm.log`.

## Dir to save the logs

use the `-d` or `--dir` options:
```
pylogrepl -d "store/logs"
pylogrepl --dir "store/logs"
```

then the log file will be in the `store/logs` directory.

## Time interval to collect errors of logrepl

We found that if something goes wrong in `logrepl`, it may produce many highly repeatitive exceptions is a short time. To avoid getting overwhelmed by those error messages, `logrepl` will collect them in a time interval and then print the non-duplicated ones. To set the time interval (although it should be non-necessary), use the '-t' or '--time' options:

```
pylogrepl -t 1.5
pylogrepl --time 1.5
```

the unit is in second.

## By .pylogrepl file

You can also sepcify the prefix & the directory by making a `.pylogrepl` in the working directory:

```
dir=logs
prefix=my_prefix
err_acc_time=1.5
```

note that the command line arguments are prioritized over the settings in `.pylogrepl`. We recommend such an approach:

- specifying `dir` in `.pylogrepl`.
- specifying `prefix` by command line argument

since you may want to change the `prefix` frequently but not the `dir`.

# APIs

By executing `pylogrepl`, the `logrepl_handler` of class `logrepl.Handler` will be loaded to the current namespace. The `logrepl_handler` controls the logging behavior of the repl.

## update logging dir / file

**logrepl.Handler.set_dir(log_dir)**

Update new logging dir. `log_dir` must be `string` or `Path`. The suffix `_yyyymmddhhmm.log` will also be updated while the `prefix` will remain unchanged.

**logrepl.Handler.set_prefix(prefix)**

Update new prefix for the log file. `prefix` sholud be `str` or `None`. The suffix `_yyyymmddhhmm.log` will also be updated while the `log_dir` will remain unchanged. Drop the prefix of new log file by setting `prefix` as `None`.

**logrepl.Handler.update_suffix()**

Update the timestamp suffix with `log_dir` & `prefix` unchanged.

## start / stop logging to file

**logrepl.Handler.start_log()**

Start logging to the file.

**logrepl.Handler.stop_log()**

Stop logging to the file.

## handle sys.stdin/stdout/stderr & builtins.input

**logrepl.Handler.set_io()**

To log **everything** of the repl, `logrepl` modifies `sys.stdin/stdout/stderr` & `builtins.input` by this method.

**logrepl.Handler.reset_io()**

Reset `sys.stdin/stdout/stderr` & `builtins.input` as-is. The input to the repl wil stil be logged into the file after executing `reset_io`.

# Notes

Exceptions ocurred when writing to the log file will not be logged since it'll lead to infinite loop.

