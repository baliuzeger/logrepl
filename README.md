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
pylogrepl -d logs
pylogrepl --dir logs
```

then the log file will be in the `logs` directory.

## By .pylogrepl file

You can also sepcify the prefix & the directory by making a `.pylogrepl` in the working directory:

```
dir=logs
prefix=my_prefix
```

note that the command line arguments are prioritized over the settings in `.pylogrepl`. We suggest that specifying `dir` in `.pylogrepl` and `prefix` by command line argument is a handy approach.

# APIs

By executing `pylogrepl`, the module `logrepl` will be loaded to the current namespace.

## update logging dir / file

**logrepl.update(prefix=None, new_dir=None)**

Update new logging dir & new prefix. When `new_dir` is not provided, the logging dir remain unchanged; when `prefix` is not provided, logs will be written to a new `yyyymmddhhmm.log`, i.e. the previous prefix will be dropped.

## start / stop logging to file

**logrepl.start_log()**

start logging to the file.

**logrepl.stop_log()**

stop logging to the file.

## Handler

**logrepl.repl_handler**

the `Handler` object that controls the logging behavior of the repl.

# Notes

Exceptions ocurred when writing to the log file will not be logged since it'll lead to infinite loop.

