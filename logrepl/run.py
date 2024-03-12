import argparse
import code
import logrepl

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="prefix for log file")
    parser.add_argument('-d', '--dir', default='.', help="dir for log file")
    args = parser.parse_args()

    if args.dir is None:
        # get from .env
        pass
    else:
        logrepl.repl_handler.set_dir(args.dir)

    logrepl.repl_handler.set_fname(args.prefix)
    logrepl.repl_handler.set_will_log(True)

    logrepl.set_io()

    dict_global = globals()

    code.interact(local=dict_global)

if __name__ == '__main__':
    main()
