import argparse
import code
import logrepl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", nargs="?", help="prefix for log file")
    parser.add_argument("-d", "--dir", help="dir for log file")
    parser.add_argument(
        "-t", "--time", help="time for accummulate logrepl error msgs"
    )
    args = parser.parse_args()

    with logrepl.log_handler(
        args.dir, args.prefix, args.time, True
    ) as logrepl_handler:
        dict_global = globals().copy()
        dict_global["logrepl_handler"] = logrepl_handler
        ls_to_pop = [
            "argparse",
            "code",
            "logrepl",
            "asyncio",
            "run_repl",
            "main",
        ]
        for k in ls_to_pop:
            dict_global.pop(k, None)
        code.interact(local=dict_global)


if __name__ == "__main__":
    main()
