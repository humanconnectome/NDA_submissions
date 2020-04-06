import pandas as pd
import yaml


class YamlSpecs:

    @staticmethod
    def load(filename='structs/asr01.yaml'):
        def rename(dictionary, old_name, new_name):
            if old_name in dictionary:
                dictionary[new_name] = dictionary.pop(old_name)

        with open(filename, 'r') as fd:
            crosswalk = yaml.load(fd.read(), yaml.SafeLoader)

        all_elements = []
        for element in crosswalk['elements']:
            element['rename'] = element['name']
            element['struct'] = crosswalk['name']
            if 'nda' in element:
                nda = element.pop('nda')
                if 'name' in nda:
                    nda['rename'] = nda.pop('name')
                if 'type' in nda:
                    nda['nda_type'] = nda.pop('type')
                element.update(nda)

            if 'redcap' in element:
                redcap = element.pop('redcap')
                sources = redcap.pop('db')
                element.update(redcap)
                for source_name, source_specific in sources.items():
                    source_specific['source'] = source_name
                    new_element = element.copy()
                    new_element.update(source_specific)
                    all_elements.append(new_element)

        df = pd.DataFrame(all_elements)
        df = df.drop(columns=['alias', 'label', 'form', 'branching', 'description', 'request'])

        funcs = {}
        for name, body in crosswalk['funcs'].items():
            funcs[name] = fn(body, 'studydata, column, converted')

        df.func = df.func.replace(funcs)

        return df


def fn(body, args='df, raw, values'):
    code = 'def func(%s):\n    ' % args
    code += body.replace('\n', '\n    ')
    new_local = {}
    exec(code, None, new_local)
    return new_local['func']

