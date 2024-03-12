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

## By .pylogrepl file

You can also sepcify the prefix & the directory by making a `.pylogrepl` in the working directory:

```
dir=logs
prefix=my_prefix
```

note that the command line arguments are prioritized over the settings in `.pylogrepl`. We suggest that specifying `dir` in `.pylogrepl` and `prefix` by command line argument everytime for your need at the moment is a handy approach.

