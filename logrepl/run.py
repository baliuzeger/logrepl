import argparse
import code
import logrepl
from dotenv import dotenv_values
import asyncio

nm_config_dir = 'dir'
nm_config_prefix = 'prefix'
default_dir = '.'
fname_config = '.pylogrepl'

async def main():
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

    if args.prefix is None and nm_config_prefix in config:
        prefix = config[nm_config_prefix]
    else:
        prefix = args.prefix

    async with logrepl.log_hanlder(
        prefix=prefix,
        log_dir=str_dir,
    ) as logrepl_handler:

        dict_global = globals()
        code.interact(local=dict_global)

if __name__ == '__main__':
    asyncio.run(main())
