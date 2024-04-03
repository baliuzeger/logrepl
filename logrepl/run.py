import argparse
import code
import logrepl
import asyncio

async def run_repl():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="prefix for log file")
    parser.add_argument('-d', '--dir', help="dir for log file")
    parser.add_argument('-t', '--time', help="time for accummulate logrepl error msgs")
    args = parser.parse_args()

    async with logrepl.log_handler(
        args.dir,
        args.prefix,
        args.time
    ) as logrepl_handler:
        logrepl_handler.set_io()
        dict_global = globals().copy()
        dict_global['logrepl_handler'] = logrepl_handler
        ls_to_pop = ['argparse', 'code', 'logrepl', 'asyncio', 'run_repl', 'main',]
        for k in ls_to_pop:
            dict_global.pop(k, None)
        code.interact(local=dict_global)

def main():
    asyncio.run(run_repl())

if __name__ == '__main__':
    main()