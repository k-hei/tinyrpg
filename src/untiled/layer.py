class Layer:

    def __init__(layer, size, data=None):
        layer._size = size
        layer._data = data or [0] * len(layer)

    @property
    def size(layer):
        return layer._size

    @property
    def data(layer):
        return layer._data

    @property
    def width(layer):
        return layer._size[0]

    @property
    def height(layer):
        return layer._size[1]

    def __len__(layer):
        return layer._size[0] * layer._size[1]

    def __getitem__(layer, cell):
        return layer._data[layer.index(cell)]

    def __setitem__(layer, cell, data):
        layer._data[layer.index(cell)] = data

    def index(layer, cell):
        col, row = cell
        return row * layer.width + col

    def fill(layer, data):
        layer._data = [data] * len(layer)

    def enumerate(layer):
        items = []
        for i, tile in enumerate(layer._data):
            col = i % layer.width
            row = i // layer.width
            cell = (col, row)
            items.append((cell, tile))
        return items
