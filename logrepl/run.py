import argparse
import code
import logrepl
import asyncio

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prefix', nargs='?', help="prefix for log file")
    parser.add_argument('-d', '--dir', help="dir for log file")
    parser.add_argument('-t', '--time', help="time for accummulate logrepl error msgs")
    args = parser.parse_args()

    async with logrepl.log_hanlder(
        args.dir,
        args.prefix,
        args.time
    ) as logrepl_handler:

        dict_global = globals()
        code.interact(local=dict_global)

if __name__ == '__main__':
    asyncio.run(main())
