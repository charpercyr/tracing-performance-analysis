
import importlib
import os


tools = None


def __load_tool(module):
    res = {}
    for a in dir(module):
        if callable(getattr(module, a)):
            res[a] = getattr(module, a)
    return res


def __load_all_tools():
    global tools
    if tools is not None:
        return
    tools = {}
    path = os.path.join(os.path.dirname(__file__), 'tools')
    for n in os.listdir(path):
        if os.path.isfile(os.path.join(path, n)):
            n = n.replace('.py', '')
            if n != '__init__':
                try:
                    tools[n] = __load_tool(importlib.import_module('generator.tools.%s' % n))
                except ImportError:
                    pass


def get_tool_names():
    __load_all_tools()
    return tools.keys()


def get_tool(name):
    __load_all_tools()
    return tools[name]


def prepare(name, parser):
    return tools[name]['prepare'](parser)


def invoke(name, func, args):
    return tools[name]['do_%s' % func](args)


if tools is None:
    __load_all_tools()
