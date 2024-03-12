import argparse
import code
import logrepl
from dotenv import dotenv_values

nm_config_dir = 'dir'
nm_config_prefix = 'prefix'
default_dir = '.'
fname_config = '.pylogrepl'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="prefix for log file")
    parser.add_argument('-d', '--dir', help="dir for log file")
    args = parser.parse_args()

    config = dotenv_values(fname_config)

    if args.dir is None:
        if nm_config_dir in config:
            str_dir = config[nm_config_dir]
        else:
            str_dir = default_dir
    else:
        str_dir = args.dir

    logrepl.repl_handler.set_dir(str_dir)

    if args.prefix is None and nm_config_prefix in config:
        prefix = config[nm_config_prefix]
    else:
        prefix = args.prefix

    logrepl.repl_handler.set_fname(prefix)

    logrepl.repl_handler.set_will_log(True)
    logrepl.set_io()

    dict_global = globals()
    code.interact(local=dict_global)

if __name__ == '__main__':
    main()
