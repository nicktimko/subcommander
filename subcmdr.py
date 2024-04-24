class Subcommander:
    """
    Self-contained copypasta class to add subcommands to a one-file Python script. 

    """
    asyncio = __import__("asyncio")
    argparse = __import__("argparse")
    dataclasses = __import__("dataclasses")
    datetime = __import__("datetime")
    inspect = __import__("inspect")
    logging = __import__("logging")
    sys = __import__("sys")
    textwrap = __import__("textwrap")
    time = __import__("time")
    typing = __import__("typing")

    def __init__(self):
        self.subcommands: self.__class__.typing.Dict[str, self.Subcommand] = {}
        self.logger = self.__class__.logging.getLogger()

    @dataclasses.dataclass
    class Arg:
        def __init__(self, *a, **kwa):
            self.args = a
            self.kwargs = kwa

        args: tuple
        kwargs: dict

    @dataclasses.dataclass
    class Subcommand:
        name: str
        func: "typing.Callable"
        wrapper_args: "tuple[tuple[typing.Any], dict[str, typing.Any]]"
        annotated_args: "dict[str, Subcommander.Arg]"
        parser: "argparse.ArgumentParser | None"

    @staticmethod
    def arg(*args, **kwargs) -> tuple[tuple, dict]:
        return args, kwargs

    @staticmethod
    def color(s, code) -> str:
        return f"\x1B[{code}m{s}\x1B[0m"

    def code(self, levelno: int) -> str:
        for level, name, colorcode in [
            (self.__class__.logging.CRITICAL, "crit", "30;41"),
            (self.__class__.logging.ERROR, "err", "91"),
            (self.__class__.logging.WARNING, "warn", "93"),
            (self.__class__.logging.INFO, "info", "92"),
            (self.__class__.logging.DEBUG, "dbug", "96"),
        ]:
            if levelno >= level:
                return self.__class__.color(format(name, "<4s"), colorcode)
        return self.__class__.color("trce", "90")

    class CLILogFmt(logging.Formatter):
        """
        info: T = 2052-03-12T02:04:12+00:00
        warn: +  0.032s something happened.
        erro: + 10.510s
        crit: +999.999s
        dbug: +1202.123s
        """

        def __init__(self, *, style="%"):
            super().__init__(style=style)
            self.start = self.__class__.time.time()
            # time.monotonic prob better, but `LogRecord.created` is time.time
            self.printed_init_time = False

        def format(self, record) -> str:
            init = ""
            if not self.printed_init_time:
                ts = self.__class__.datetime.datetime.fromtimestamp(self.start).isoformat(
                    timespec="milliseconds"
                )[11:]
                init = f"T={ts}\n"
                self.printed_init_time = True

            dt = record.created - self.start
            return (
                f"{init}{Subcommander.code(record.levelno)}: +{dt: 7.3f}s {record.msg}"
            )

    def command(self, *arg_defs):
        def _wrapper(f):
            name = f.__name__.replace("_", "-")

            sig_args = {}
            sig = self.__class__.inspect.signature(f)
            for pname, param in sig.parameters.items():
                if pname == "argns":
                    if arg_defs:
                        raise ValueError(
                            "no 'argns' argument to receive generic namespace"
                        )
                    continue
                if isinstance(param.default, self.Arg):
                    sig_args[pname] = param.default
                elif param.annotation is not self.__class__.inspect._empty:
                    sig_args[pname] = self.Arg(pname, type=param.annotation)
                else:
                    raise ValueError(
                        "named argument does not have a type annotation or Arg default",
                        pname,
                    )

            sc = self.Subcommand(
                name=name,
                func=f,
                wrapper_args=arg_defs,
                annotated_args=sig_args,
                parser=None,
            )
            self.subcommands[name] = sc
            return f

        return _wrapper

    def _run(self):
        parser = self.__class__.argparse.ArgumentParser(
            description=self.__class__.textwrap.dedent(__doc__),
            formatter_class=self.__class__.argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("-v", "--verbose", action="count", default=0)
        subparsers = parser.add_subparsers(required=True)

        for name, sc_data in self.subcommands.items():
            subcmd_parser = subparsers.add_parser(name, help=sc_data.func.__doc__)
            for args, kwargs in sc_data.wrapper_args:
                subcmd_parser.add_argument(*args, **kwargs)
            for name, argc in sc_data.annotated_args.items():
                if not argc.args:
                    argc.args = (name,)
                subcmd_parser.add_argument(*argc.args, **argc.kwargs)
            subcmd_parser.set_defaults(func=sc_data.func)

        args = parser.parse_args()

        loglevel = {
            0: self.__class__.logging.WARNING,
            1: self.__class__.logging.INFO,
            2: self.__class__.logging.DEBUG,
        }.get(args.verbose, self.__class__.logging.DEBUG)

        L = self.__class__.logging.getLogger("main")
        handler = self.__class__.logging.StreamHandler(stream=sys.stderr)
        cli_fmt = self.CLILogFmt()
        handler.setFormatter(cli_fmt)
        L.addHandler(handler)
        L.setLevel(loglevel)

        if self.__class__.inspect.iscoroutinefunction(args.func):
            retval = self.__class__.asyncio.run(args.func(args))
        else:
            retval = args.func(args)
        return retval

    def run(self):
        self.__class__.sys.exit(self._run())

