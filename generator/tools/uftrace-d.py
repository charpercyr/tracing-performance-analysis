
import generator.generic as generic


def prepare(parser):
    import generator.loader as loader
    loader.prepare('uftrace', parser)


def do_generate(args):
    generic.generic_generate(args)


def do_compile(args):
    import generator.loader as loader
    loader.invoke('uftrace', 'compile', args)


def do_run(args):
    generic.generic_run(args)


def do_clean(args):
    generic.generic_clean(args)
