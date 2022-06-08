class Layer:

    def __init__(layer, size, data):
        layer._size = size
        layer._data = data

    @property
    def size(layer):
        return layer._size

    @property
    def width(layer):
        return layer._size[0]

    @property
    def height(layer):
        return layer._size[1]

    def __getitem__(layer, cell):
        col, row = cell
        index = row * layer.width + col
        return layer._data[index]

    def enumerate(layer):
        items = []
        for i, tile in enumerate(layer._data):
            col = i % layer.width
            row = i // layer.width
            cell = (col, row)
            items.append((cell, tile))
        return items
