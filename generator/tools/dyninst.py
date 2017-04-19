
import os
import subprocess as sp

import generator.generic as generic


def prepare(parser):
    generic.generic_prepare(parser)


def do_generate(args):
    generic.generic_generate(args)


def do_compile(args):
    args.cflags += ['-g']
    args.ldflags += ['-g']
    generic.generic_compile(args)


def do_run(args):

    if os.geteuid() != 0:
        raise OSError('Run this script as root')

    env = {k: os.environ[k] for k in os.environ}
    env['DYNINSTAPI_RT_LIB'] = '/usr/local/lib/libdyninstAPI_RT.so'
    env['LD_LIBRARY_PATH'] = '/usr/local/lib:/usr/lib/'
    env['LD_PRELOAD'] = '/usr/local/lib/liblttng-ust.so'

    args.env += ['DYNINSTAPI_RT_LIB=/usr/local/lib/libdyninstAPI_RT.so']
    args.env += ['LD_LIBRARY_PATH=/usr/local/lib:/usr/lib/']
    args.env += ['LD_PRELOAD=liblttng-ust.so']

    compile_args = generic.generic_run_preset(args)[0]
    exe_name = generic.get_exe_name(compile_args.main, compile_args.func, compile_args.steps,
                                    compile_args.iter, compile_args.count, compile_args.nthreads, '')

    def before():
        sp.call(['lttng-sessiond', '--daemonize'], env=env)
        sp.call(['lttng', 'create', 'projet4', '-o', 'dyninst.out/%s/trace' % args.preset], env=env)
        sp.call(['lttng', 'enable-event', '-u', 'dyn-tp:test_0', '--session=projet4',
                 '--function', '%s@test_0' % exe_name], env=env)
        sp.call(['lttng', 'start', 'projet4'], env=env)

    def after():
        sp.call(['lttng', 'destroy', 'projet4'], env=env)
        sp.call(['pkill', 'lttng'])

    generic.generic_run(args, pre_call=before, post_call=after)


def do_clean(args):
    generic.generic_clean(args)
