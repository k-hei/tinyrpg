added_files = {
    'assets/*.png': 'assets',
    'assets/*.json': 'assets',
    'assets/pngfont/*': 'assets/pngfont',
    'assets/ttf/*': 'assets/ttf',
    'rooms/*': 'rooms',
    'src/data00.json': 'src',
    'src/locations/elems/*': 'src/locations/elems',
    'VERSION': '.',
}


def format_spec_buffer(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as spec_file:
            spec_buffer = spec_file.read()
    except FileNotFoundError:
        spec_buffer = ''

    spec_buffer = replace_spec_buffer(spec_buffer)

    try:
        with open(file_path, mode='w', encoding='utf-8') as spec_file:
            spec_file.write(spec_buffer)
    except FileNotFoundError:
        pass


def replace_spec_buffer(spec_buffer):
    if not spec_buffer:
        return ''

    pattern = 'pyz = PYZ'
    return spec_buffer.replace(
        pattern,
        f'\na.datas = {list(added_files.items())}\n\n{pattern}'
    )


def main():
    print(' '.join([f'--add-data {src};{dest}'
        for src, dest in added_files.items()]))


if __name__ == '__main__':
    main()
