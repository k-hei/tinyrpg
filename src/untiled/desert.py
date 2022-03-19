from untiled import TilesetProcessor
from PIL import Image, ImageOps


tile_size = 16
tileset_path = "assets/desert-tiles.png"
tileset_image = Image.open(tileset_path)
tileset_cols = tileset_image.width // tile_size
tileset_rows = tileset_image.height // tile_size
tile_map = {}
rect_map = {}
tile_ids = range(tileset_cols * tileset_rows)

for tile_id in tile_ids:
    tile_col = (tile_id) % tileset_cols
    tile_row = (tile_id) // tileset_cols
    tile_rect = (
        tile_col * tile_size, tile_row * tile_size,
        (tile_col + 1) * tile_size, (tile_row + 1) * tile_size
    )
    tile_map[tile_id] = tileset_image.crop(tile_rect)
    rect_map[tile_id] = tile_rect


MASK_HORIZ = 0x80000000
MASK_VERT = 0x40000000
MASK_DIAG = 0x20000000
transform_map = {
    MASK_HORIZ + MASK_VERT + MASK_DIAG: lambda image: (
        ImageOps.mirror(image).transpose(Image.ROTATE_90)
    ),
    MASK_HORIZ + MASK_VERT: lambda image: (
        image.transpose(Image.ROTATE_180)
    ),
    MASK_HORIZ + MASK_DIAG: lambda image: (
        image.transpose(Image.ROTATE_270)
    ),
    MASK_HORIZ: lambda image: (
        image.transpose(Image.FLIP_LEFT_RIGHT)
    ),
    MASK_VERT + MASK_DIAG: lambda image: (
        image.transpose(Image.ROTATE_90)
    ),
    MASK_VERT: lambda image: (
        image.transpose(Image.FLIP_TOP_BOTTOM)
    ),
    MASK_DIAG: lambda image: (
        image.transpose(Image.TRANSVERSE).transpose(Image.ROTATE_180)
    ),
    0: lambda image: image,
}

def transform_image(image, mask):
    return transform_map[mask](image)


class DesertProcessor(TilesetProcessor):

    @classmethod
    def process(cls, layer, image=None):
        layer_width, layer_height = cls.get_layer_dimensions(layer)
        layer_image = image or Image.new(
            mode="RGBA",
            size=(layer_width * tile_size, layer_height * tile_size)
        )

        for row in range(layer_height):
            for col in range(layer_width):
                tile_id = layer[row][col]
                if tile_id == -1:
                    continue

                rotation_mask = tile_id & 0xff000000
                if rotation_mask:
                    tile_id &= 0x00ffffff

                tile_image = tile_map[tile_id]
                tile_image = transform_image(tile_image, rotation_mask)
                layer_image.paste(tile_image, (col * tile_size, row * tile_size), tile_image)

        return layer_image
