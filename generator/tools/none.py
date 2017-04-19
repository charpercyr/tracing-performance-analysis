
import generator.generic as generic


def prepare(parser):
    generic.generic_prepare(parser)


def do_generate(args):
    generic.generic_generate(args)


def do_compile(args):
    generic.generic_compile(args)


def do_run(args):
    generic.generic_run(args)


def do_clean(args):
    generic.generic_clean(args)
