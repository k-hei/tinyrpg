class Tileset:

    def __init__(tileset, size, image):
        tileset._size = size
        tileset._image = image
        tileset._tiles = None
        tileset._setup()

    def _setup(tileset):
        tile_size = tileset._size
        tileset_image = tileset._image

        tileset_cols = tileset_image.width // tile_size
        tileset_rows = tileset_image.height // tile_size
        tile_map = {}
        tile_ids = range(tileset_cols * tileset_rows)

        for tile_id in tile_ids:
            tile_col = (tile_id) % tileset_cols
            tile_row = (tile_id) // tileset_cols
            tile_rect = (
                tile_col * tile_size, tile_row * tile_size,
                (tile_col + 1) * tile_size, (tile_row + 1) * tile_size
            )
            tile_map[tile_id] = tileset_image.crop(tile_rect)

        tileset._tiles = tile_map

    @property
    def tile_size(tileset):
        return tileset._size

    def get(tileset, id):
        return tileset._tiles[id]
