import argparse
import json
from jsonschema import validate
from shutil import copy2
import sys


SETTINGS_FILE = 'settings.tex'
SCHEMA_FILE = 'schema.json'


def copy_settings(out_file):
    copy2(SETTINGS_FILE, out_file)


def handle_top(name):
    lines = []
    lines.append('%................ DOCUMENT ................')
    lines.append('\\begin{document}')
    lines.append('\\noindent\\hfil \\textbf{\\textsc{\\Large %s}}\\hfil' % name)
    lines.append('')
    lines.append('\\vspace{-10mm}')
    return lines


def _get_section_lines(items, left='', right=''):
    lines = []
    lines.append('\\section*{}')

    for i, line in enumerate(items):
        if i == 0:
            lines.append('%s %s%s' % (left, line, right))
            continue
        lines.append('')
        lines.append('\\noindent%s %s%s' % (left, line, right))

    return lines


def handle_header(header):
    lines = []

    if 'left' not in header or 'middle' not in header or 'right' not in header:
        return lines

    lines.append('\\begin{multicols}{3}')
    lines.extend(_get_section_lines(header['left']))
    lines.extend(_get_section_lines(header['middle'], '\\hfil', '\\hfil'))
    lines.extend(_get_section_lines(header['right'], '\\hfill'))
    
    lines.append('\\end{multicols}')
    lines.append('\\smallskip')
    lines.append('')

    return lines


def _handle_category(name):
    lines = []
    lines.append('\\noindent\\textbf{\\textsc{%s}}\\\\' % name)
    lines.append('\\rule{\\textwidth}{1pt}\\\\')
    return lines


def _description_generator(descriptions, ignore):
    i = 0

    while i < len(descriptions):
        if i in ignore:
            i += 1
            continue
        yield descriptions[i]
        i += 1

    while i < 1:
        yield ''
        i += 1

def _handle_item_data(item):
    lines = []

    if 'disabled' in item and item['disabled']:
        return lines

    lines.append('\\noindent\\resumeentry{\\textbf{%s}}{\\textbf{%s}}' %
        (item['title'], item.get('location', '')))
    lines.append('')
    
    try:
        ignore = item['ignore']
    except KeyError:
        ignore = []

    desc = _description_generator(item['description'], ignore)

    if 'position' in item:
        lines.append('\\noindent\\resumeentry{\\textit{%s}}{\\textit{%s}}' %
            (item['position'], item.get('date', '')))
    else:
        lines.append('\\resumeentry{%s}{\\textit{%s}}' %
            (next(desc), item.get('date', '')))

    for val in desc:
        lines.append('')
        lines.append('\\resumeentry{%s}{}' % val)

    lines.append('\\smallskip')
    lines.append('')
    
    return lines


def _handle_section(data):
    lines = []

    if 'disabled' in data and data['disabled']:
        return lines

    lines.extend(_handle_category(data['category']))

    for item in data['items']:
        lines.extend(_handle_item_data(item))

    return lines


if __name__ == '__main__':
    schema = file(SCHEMA_FILE)
    schema_validate = json.load(schema)

    usage = '%prog [options] input_file output_file'
    parser = argparse.ArgumentParser(usage=usage)

    parser.add_argument('in_file', help='JSON file with resume info.')
    parser.add_argument('out_file', help='Destination of created tex file.')

    args = parser.parse_args()
    
    in_file = file(args.in_file)
    vals = json.load(in_file)

    try:
        validate(vals, schema_validate)
    except ValidationError:
        print 'Please check the JSON schema!'
        sys.exit(1)

    output = handle_top(vals['name'])
    output.extend(handle_header(vals['header']))

    for section in vals['sections']:
        output.extend(_handle_section(section))

    output.append('\\end{document}')

    copy_settings(args.out_file)

    with open(args.out_file, 'a+') as out:
        out.write('\n'.join(output))

    print 'Done!'
