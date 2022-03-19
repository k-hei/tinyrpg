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


class DesertProcessor(TilesetProcessor):

    @classmethod
    def process(cls, layer):
        layer_width, layer_height = cls.get_layer_dimensions(layer)
        layer_image = Image.new(mode="RGBA", size=(layer_width * tile_size, layer_height * tile_size))
        for row in range(layer_height):
            for col in range(layer_width):
                tile_id = layer[row][col]
                # tile_id = max(0, tile_id - 1)
                rotation_mask = tile_id & 0xff000000
                rotation_mask_orig = rotation_mask
                masks = []
                if rotation_mask:
                    tile_id &= 0x0000ffff
                    tile_image = tile_map[tile_id]

                    MASK_HORIZ = 0x80000000
                    MASK_VERT = 0x40000000
                    MASK_DIAG = 0x20000000
                    MASK_HORIZVERTDIAG = MASK_HORIZ + MASK_VERT + MASK_DIAG
                    MASK_HORIZVERT = MASK_HORIZ + MASK_VERT
                    MASK_HORIZDIAG = MASK_HORIZ + MASK_DIAG
                    MASK_VERTDIAG = MASK_VERT + MASK_DIAG

                    if rotation_mask >= MASK_HORIZVERTDIAG:
                        tile_image = tile_image.transpose(Image.ROTATE_90)
                        tile_image = ImageOps.mirror(tile_image)
                        rotation_mask -= MASK_HORIZVERTDIAG
                        masks.append("HVD")

                    if rotation_mask >= MASK_HORIZVERT:
                        tile_image = tile_image.transpose(Image.ROTATE_180)
                        rotation_mask -= MASK_HORIZVERT
                        masks.append("HV")

                    if rotation_mask >= MASK_HORIZDIAG:
                        tile_image = tile_image.transpose(Image.ROTATE_270)
                        rotation_mask -= MASK_HORIZDIAG
                        masks.append("HD")

                    if rotation_mask >= MASK_HORIZ:
                        tile_image = ImageOps.mirror(tile_image)
                        rotation_mask -= MASK_HORIZ
                        masks.append("H")

                    if rotation_mask >= MASK_VERTDIAG:
                        tile_image = tile_image.transpose(Image.ROTATE_90)
                        rotation_mask -= MASK_VERTDIAG
                        masks.append("VD")

                    if rotation_mask >= MASK_VERT:
                        tile_image = ImageOps.flip(tile_image)
                        rotation_mask -= MASK_VERT
                        masks.append("V")

                    if rotation_mask >= MASK_DIAG:
                        tile_image = tile_image.transpose(Image.TRANSVERSE)
                        tile_image = tile_image.transpose(Image.ROTATE_180)
                        rotation_mask -= MASK_DIAG
                        masks.append("D")
                else:
                    tile_image = tile_map[tile_id]

                print((col, row), tile_id, end=" ")
                print(rect_map[tile_id], hex(rotation_mask_orig), ", ".join(masks))
                layer_image.paste(tile_image, (col * tile_size, row * tile_size))

        layer_image.save("output.png")
