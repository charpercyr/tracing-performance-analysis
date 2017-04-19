
import generator.generic as generic


def prepare(parser):
    generic.generic_prepare(parser)


def do_generate(args):
    generic.generic_generate(args)


def do_compile(args):
    args.cflags += ['-pg', '-mfentry', '-mnop-mcount']
    generic.generic_compile(args)


def do_run(args):
    if args.inactive:
        funcargs = ()
    else:
        compile_args = generic.generic_run_preset(args)
        function_names = [f[1] for f in generic.get_function_names(compile_args[0].count)]
        funcargs = ('-P', *function_names)
    generic.generic_run(args, ('uftrace', '--force', *funcargs))


def do_clean(args):
    generic.generic_clean(args)
