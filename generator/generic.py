
import csv
import os
import shutil
import subprocess as sp
import time

from generator.loader import invoke


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
FUNC_DIR = os.path.join(TEMPLATE_DIR, 'func')
MAIN_DIR = os.path.join(TEMPLATE_DIR, 'main')
FUNC_H_FILE = os.path.join(TEMPLATE_DIR, 'func.h')
FUNC_C_FILE = os.path.join(TEMPLATE_DIR, 'func.c')


def get_c_names(main, func, steps, iterations, count, nthreads, output_dir):
    main_name = os.path.join(output_dir, 'src', '%s_%d_%d_%d_%d_main.c' % (main, steps, iterations, count, nthreads))
    func_name_c = os.path.join(output_dir, 'src', '%s_%d_func.c' % (func, count))
    func_name_h = os.path.join(output_dir, 'src', '%s_%d_func.h' % (func, count))
    return main_name, func_name_c, func_name_h


def get_exe_name(main, func, steps, iterations, count, nthreads, output_dir):
    return os.path.join(output_dir, '%s_%s_%d_%d_%d_%d' % (main, func, steps, iterations, nthreads, count))


def get_output_dir(tool, inactive):
    return '%s%s.out' % (tool, '-d' if inactive else '')


def get_function_names(count):
    return [(i, 'test_%d' % i) for i in range(count)]


def generate_str(in_str, variables):
    for v in variables:
        if '%s%{}%%'.format(v) in in_str:
            in_str = in_str.replace('%s%{}%%'.format(v), str(variables[v]))
        elif '%d%{}%%'.format(v) in in_str:
            in_str = in_str.replace('%d%{}%%'.format(v), str(int(variables[v])))
    return in_str


def generate_file(in_str, out_name, variables):
    if not os.path.exists(os.path.dirname(out_name)):
        os.makedirs(os.path.dirname(out_name))
    out = open(out_name, 'w')
    out.write(generate_str(in_str, variables))


def do_generate(main, func, steps, iterations, count, nthreads, args):
    output_dir = get_output_dir(args.tool, args.inactive)

    main_file = open(os.path.join(MAIN_DIR, '%s.c' % main)).read()
    func_c_temp = open(os.path.join(FUNC_DIR, '%s.c' % func)).read()
    func_h_file = open(FUNC_H_FILE).read()
    func_c_file = open(FUNC_C_FILE).read()

    main_name, func_c_name, func_h_name = get_c_names(main, func, steps, iterations, count, nthreads, output_dir)

    function_names = get_function_names(count)

    if main_name is not None:
        main_vars = {
            'funch': os.path.basename(func_h_name),
            'testid': '%s_%s_%d_%d_%d_%d' % (main, func, steps, iterations, count, nthreads),
            'nsteps': steps,
            'niter': iterations,
            'nthreads': nthreads,
            'callfuncs': '\n'.join('%s(i);' % n[1] for n in function_names)
        }
        generate_file(main_file, main_name, main_vars)

    if func_h_name is not None:
        func_h_vars = {
            'funch': os.path.basename(func_h_name).replace('.', '_').upper(),
            'declfuncs': '\n'.join('void %s(int iter);' % n[1] for n in function_names)
        }
        generate_file(func_h_file, func_h_name, func_h_vars)

    if func_c_name is not None:
        func_c_vars = {
            'funch': os.path.basename(func_h_name),
            'deffuncs': '\n\n\n'.join('%s' % (generate_str(func_c_temp, {'funcidx': n[0], 'funcname': n[1]}))
                                      for n in function_names)
        }
        generate_file(func_c_file, func_c_name, func_c_vars)


def do_compile(main, func, steps, iterations, count, nthreads, args):

    output_dir = get_output_dir(args.tool, args.inactive)

    c_names = get_c_names(main, func, steps, iterations, count, nthreads, output_dir)

    o_names = {n: n.replace('.c', '.o').replace('/src', '/obj') for n in c_names if n.endswith('.c')}

    if not os.path.exists(os.path.join(output_dir, 'obj')):
        os.makedirs(os.path.join(output_dir, 'obj'))

    start = time.time()
    for n in o_names:
        sp.call(['gcc'] + args.cflags + ['-c', n, '-o', o_names[n]])

    exe_name = get_exe_name(main, func, steps, iterations, count, nthreads, output_dir)
    sp.call(['gcc'] + args.ldflags + [o_names[n] for n in o_names] + ['-o', exe_name] + args.libs + ['-lpthread'])
    end = time.time()
    return end - start


def __get_template_list(name):
    res = []
    for f in os.listdir(os.path.join(os.path.dirname(__file__), 'templates', name)):
        if f.endswith('.c'):
            res += [f[:-2]]
    return res


def __prepare_generate(parser):
    parser.add_argument('main', choices=__get_template_list('main'), help='Main template to use')
    parser.add_argument('func', choices=__get_template_list('func'), help='Function template to use')
    parser.add_argument('-s', '--steps', type=int, help='Number of steps to execute', default=1)
    parser.add_argument('-i', '--iter', type=int, help='Number of iterations to execute at each step', default=1000)
    parser.add_argument('-c', '--count', type=int, help='Number of functions to generate', default=1)
    parser.add_argument('-t', '--threads', dest='nthreads', type=int, help='Number of threads to run', default=1)
    parser.add_argument('--inactive', action='store_true',
                        help='Use this to start/compile the application without tracing active')


def generic_prepare(parser):
    sp = parser.add_subparsers()

    generate_parser = sp.add_parser('generate')
    compile_parser = sp.add_parser('compile')
    clean_parser = sp.add_parser('clean')
    run_parser = sp.add_parser('run')

    __prepare_generate(generate_parser)
    __prepare_generate(compile_parser)

    compile_parser.add_argument('--cflags', nargs='*', help='Additional gcc flags to use during compile', default=[])
    compile_parser.add_argument('--ldflags', nargs='*', help='Additional gcc flags to use during linking', default=[])
    compile_parser.add_argument('--libs', nargs='*', help='Additional libraries to link', default=[])

    run_parser.add_argument('preset', choices=['time', 'memory', 'compile-time', 'start-time', 'all'])
    run_parser.add_argument('--env', nargs='*', help='Environment variables to set', default=[])
    run_parser.add_argument('--compile-steps', help='Number of steps for compile-time preset', default=5, type=int)
    run_parser.add_argument('--compile-iter', help='Number of iteration per step for compile-time preset',
                            default=10, type=int)
    run_parser.add_argument('--threads', dest='nthreads', help='Number of threads to run', default=1, type=int)
    run_parser.add_argument('--inactive', action='store_true',
                        help='Use this to start/compile the application without tracing active')

    generate_parser.set_defaults(step='generate')
    compile_parser.set_defaults(step='compile')
    clean_parser.set_defaults(step='clean')
    run_parser.set_defaults(step='run')

    return generate_parser, compile_parser, clean_parser, run_parser, sp


def generic_generate(args):
    return do_generate(args.main, args.func, args.steps, args.iter, args.count, args.nthreads, args)


def generic_compile(args):
    invoke(args.tool, 'generate', args)
    return do_compile(args.main, args.func, args.steps, args.iter, args.count, args.nthreads, args)


def generic_clean(args):
    try:
        inactive = args.inactive
    except AttributeError:
        inactive = False
    output_dir = get_output_dir(args.tool, inactive)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)


class CompileArgs:
    def __init__(self, tool, preset, cflags, ldflags, libs, main, func, steps, iter, count, nthreads, inactive, args):
        self.tool = tool
        self.preset = preset
        self.cflags = cflags
        self.ldflags = ldflags
        self.libs = libs
        self.main = main
        self.func = func
        self.steps = steps
        self.iter = iter
        self.count = count
        self.nthreads = nthreads
        self.inactive = inactive
        for k in dir(args):
            self.__dict__[k] = getattr(args, k)


def generic_run_preset(args):
    if args.preset == 'time':
        compile_args = [
            CompileArgs(args.tool, args.preset, [], [], [], 'time', 'inc', 5, 2**24, 1, 1, args.inactive, args)
        ]
    elif args.preset == 'memory':
        compile_args = [
            CompileArgs(args.tool, args.preset, [], [], [], 'normal', 'inc', 5, 2**24, 1, 1, args.inactive, args)
        ]
    elif args.preset == 'start-time':
        compile_args = [
            CompileArgs(args.tool, args.preset, [], [], [], 'normal', 'inc', 5, 1, 1, 1, args.inactive, args)
        ]
    elif args.preset == 'all':
        compile_args = []
        args.preset = 'time'
        compile_args += generic_run_preset(args)
        args.preset = 'memory'
        compile_args += generic_run_preset(args)
        args.preset = 'start-time'
        compile_args += generic_run_preset(args)
        args.preset = 'all'
    else:
        raise RuntimeError('Not supposed to be here')
    return compile_args


def generic_run(args, pre_exe=(), post_exe=(), pre_call=None, post_call=None):
    env = {k: os.environ[k] for k in os.environ}
    for v in args.env:
        k, v = v.split('=')
        env[k] = v

    output_dir = get_output_dir(args.tool, args.inactive)

    all_compile_args = generic_run_preset(args)

    for compile_args in all_compile_args:
        cwd = './%s/%s' % (output_dir, compile_args.preset)
        if os.path.isdir(cwd):
            shutil.rmtree(cwd)
        os.makedirs(cwd)
        invoke(args.tool, 'compile', compile_args)
        exe_name = get_exe_name(compile_args.main,
                                compile_args.func,
                                compile_args.steps,
                                compile_args.iter,
                                compile_args.count,
                                compile_args.nthreads,
                                '..')

        stdout = open('%s/%s/stdout' % (output_dir, compile_args.preset), 'wb')
        stderr = open('%s/%s/stderr' % (output_dir, compile_args.preset), 'wb')

        if pre_call:
            pre_call()

        if compile_args.preset == 'time':
            sp.call([*pre_exe, exe_name, *post_exe], env=env, stdout=stdout, stderr=stderr, cwd=cwd)
        elif compile_args.preset == 'memory':
            sp.call(['valgrind', '--tool=massif', '--time-unit=B', *pre_exe, exe_name, *post_exe],
                    env=env, stdout=stdout, stderr=stderr, cwd=cwd)
        elif compile_args.preset == 'start-time':
            writer = csv.writer(open('%s/start-time/data.csv' % output_dir, 'w'))
            writer.writerow(['Step', 'Time', 'Iterations'])
            for i in range(compile_args.steps):
                start = time.time()
                for _ in range(compile_args.iter):
                    sp.call([*pre_exe, exe_name, *post_exe], env=env, stdout=stdout, stderr=stderr, cwd=cwd)
                end = time.time()
                writer.writerow([i, end-start, compile_args.iter])

        if post_call:
            post_call()
