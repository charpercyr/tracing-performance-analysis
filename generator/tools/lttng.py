import subprocess as sp

import generator.generic as generic


def prepare(parser):
    _, compile_parser, _, run_parser, sp = generic.generic_prepare(parser)

    compile_parser.add_argument('--preload', action='store_true',
                                help='Use this to use LD_PRELOAD instead of linking the library')

    run_parser.add_argument('--preload', action='store_true',
                            help='Use this to use LD_PRELOAD instead of linking the library')


def do_generate(args):
    generic.generic_generate(args)


def do_compile(args):
    args.cflags += ['-finstrument-functions', '-finstrument-functions-exclude-function-list=main']
    if not args.preload:
        args.libs += ['-llttng-ust-cyg-profile-fast']
    return generic.generic_compile(args)


def do_run(args):

    if args.preload:
        args.env += ['LD_PRELOAD=liblttng-ust-cyg-profile.so']

    if not args.inactive:
        def pre_call():
            if args.preset != 'compile-time':
                sp.call(['lttng', 'create', 'projet4', '-o', 'lttng.out/%s/trace' % args.preset])
                sp.call(['lttng', 'enable-event', '-u', 'lttng_ust_cyg_profile:*', '--session=projet4'])
                sp.call(['lttng', 'start', 'projet4'])

        def post_call():
            if args.preset != 'compile-time':
                sp.call(['lttng', 'destroy', 'projet4'])
    else:
        pre_call = None
        post_call = None

    generic.generic_run(args, pre_call=pre_call, post_call=post_call)


def do_clean(args):
    generic.generic_clean(args)