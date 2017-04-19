
import argparse


def main():
    import generator.loader as loader

    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers()

    for t in loader.get_tool_names():
        p = sp.add_parser(t)
        loader.prepare(t, p)
        p.set_defaults(tool=t)

    args = parser.parse_args()

    if not hasattr(args, 'tool') or not hasattr(args, 'step'):
        parser.print_help()
        exit(1)

    loader.invoke(args.tool, args.step, args)

if __name__ == '__main__':
    main()
