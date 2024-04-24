from subcmdr import Subcommander

### The above is intended to be replaced by the copypasta
s = Subcommander()

import argparse
import datetime

@s.command(
    s.arg(
        "format",
        help="Formatting string",
    ),
)
def time1(args: argparse.Namespace):
    now = datetime.datetime.now()
    fmtd = now.strftime(args.format)
    print(fmtd)


@s.command()
def time2(format: str = s.Arg(help="formatting string")):
    now = datetime.datetime.now()
    fmtd = now.strftime(format)
    print(fmtd)


if __name__ == "__main__":
    s.run()
