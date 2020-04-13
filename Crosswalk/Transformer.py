import os
import yaml
from collections import defaultdict
import pandas as pd

from libs.YamlCache import YamlCache


def aslist(item):
    if not item:
        return []
    elif type(item) is list:
        return item
    else:
        return [item]


def xyz(body, n=1):
    args = ', '.join(list('xXyYzZ')[:n * 2])
    code = 'def func(%s):\n    ' % args
    code += body.replace('\n', '\n    ')
    new_local = {}
    exec(code, None, new_local)
    return new_local['func']


def passthrough(x, X, y=None, Y=None, z=None, Z=None):
    return x, y, z


class Transformer:
    def __init__(self, map_dir='./map/', funcs={}):
        self.y = YamlCache()
        self.funcs = funcs
        self.writer = None
        self.map_dir = map_dir
        self.elements = []
        self.mappings = {}
        self.load_maps()

    def load_map(self, struct):
        filepath = os.path.join(self.map_dir, struct + '.yaml')
        contents = self.y.load(filepath)
        element_list = contents['elements']

        elements = []
        for item in element_list:
            item['struct'] = struct
            sources_list = item.pop('source')
            for source in sources_list:
                new_element = item.copy()
                elements.append(new_element)

                if type(source) is str:
                    new_element['source'] = source
                else:
                    new_element['source'], additional_detail = source.popitem()
                    new_element.update(additional_detail)
        self.elements.extend(elements)
        return elements

    def load_maps(self, path=None):
        path = path if path else self.map_dir
        for filename in os.listdir(path):
            if filename.endswith('.yaml'):
                self.load_map(filename[:-5])

    def get_unique_variables(self):
        unique = set()
        for e in self.elements:
            names = e.get('name')
            source = e.get('source')
            struct = e.get('struct')

            if type(names) is str:
                unique.add((source, names))
            elif type(names) is list:
                unique.update([(source, name) for name in names])
        return unique

    def get_executable(self, element, nargs):
        code, func = element.get('code'), element.get('func')
        if func:
            if func in self.funcs:
                executable = self.funcs[func]
            else:
                print('There is no function of that name so just passing through.', func)
                executable = passthrough
        elif code:
            executable = xyz(code, nargs)
        else:
            executable = passthrough
        return executable

    def transform(self, datacache, filter_fn=None):
        db = defaultdict(lambda: defaultdict(dict))
        for e in filter(filter_fn, self.elements):
            struct, source, = e['struct'], e['source']
            column = db[struct][source]
            renames = aslist(e.get('rename'))
            names = aslist(e.get('name'))
            data = datacache.get_fields(source, names)

            if 'recode' in e:
                data[0].replace(e['recode'], inplace=True)

            func = self.get_executable(e, len(names))
            result = func(*data)
            if type(result) is not tuple:
                result = (result,)

            for i in range(min(len(result), len(renames))):
                column[renames[i]] = result[i]

        result = {}
        for struct, v1 in db.items():
            result[struct] = pd.concat(list(map(pd.DataFrame, v1.values())))

        return result
