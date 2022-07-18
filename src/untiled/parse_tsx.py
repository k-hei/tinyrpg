import sys
import xml.etree.ElementTree as ElementTree


def parse_tsx_from_path(tsx_path):
    try:
        with open(tsx_path, mode='r', encoding='utf-8') as tsx_file:
            tsx_buffer = tsx_file.read()
    except FileNotFoundError:
        tsx_buffer = ''

    return parse_tsx_from_buffer(tsx_buffer)

def parse_tsx_from_buffer(tsx_buffer):
    root = ElementTree.fromstring(tsx_buffer)

    image_paths = [child[0].attrib['source'] for child in root[1:]]
    return image_paths

def main(tsx_path):
    parse_tsx_from_path(tsx_path)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: python3 src/untiled/parse_tsx.py foo.tsx')
        sys.exit()

    main(tsx_path=sys.argv[1])
