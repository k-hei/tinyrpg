from lib.grid import Grid


class TileMatrix:
    """
    Wraps multiple layers into a cohesive interface.
    """

    # TODO: use size and data list (implementation detail -- interface should remain unchanged)
    _layers: list[Grid]

    def __init__(matrix, layers):
        matrix._layers = layers

    @property
    def num_layers(matrix):
        return len(matrix._layers)

    def __getitem__(matrix, cell):
        """
        Gets the list of tiles at the given cell.
        """
        return [layer[cell] for layer in matrix._layers]

    def __contains__(matrix, cell):
        return matrix._layers[0].contains(*cell)

    # TODO: remove
    def contains(matrix, x, y):
        return (x, y) in matrix

    def enumerate(matrix):
        return matrix._layers[0].enumerate()

    def is_cell_walkable(matrix, cell):
        return not next((not layer[cell] for layer in matrix._layers), None)
