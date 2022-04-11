import json
from PIL import Image
from untiled import TilesetProcessor
from untiled.tileset import Tileset
from untiled.transform import transform_image, extract_transform_mask, MASK_HORIZ
from untiled.layer import Layer
from locations.desert.tiles import DesertTileset
import assets

TILE_SIZE = 16
tileset = Tileset(
    size=TILE_SIZE,
    image=Image.open("assets/desert-tiles.png")
)

def load_elems(file_path):
    with open(file_path, mode="r", encoding="utf-8") as file:
        file_buffer = file.read()
    return json.loads(file_buffer)

elems = load_elems(file_path=DesertTileset.elems_path)


class DesertProcessor(TilesetProcessor):

    @staticmethod
    def resolve_tile_image_from_id(tile_id):
        tile_id, transform_mask = extract_transform_mask(tile_id)
        tile_image = tileset[tile_id]
        tile_image = transform_image(tile_image, transform_mask)
        return tile_image

    @staticmethod
    def process_layer(layer, image=None):
        layer_width, layer_height = layer.size
        layer_image = image or Image.new(
            mode="RGBA",
            size=(layer_width * tileset.tile_size, layer_height * tileset.tile_size)
        )
        return layer_image

    @classmethod
    def process_tile_layer(cls, layer, image=None):
        layer_image = DesertProcessor.process_layer(layer, image)

        for (col, row), tile_id in layer.enumerate():
            if tile_id == -1:
                continue

            tile_image = cls.resolve_tile_image_from_id(tile_id)
            layer_image.paste(
                tile_image,
                (col * tileset.tile_size, row * tileset.tile_size),
                mask=tile_image
            )

        return layer_image

    @classmethod
    def process_object_layer(cls, layer, image):
        layer_elems = []
        layer_data = Layer(size=layer.size)
        layer_data.fill(-1)
        visited_cells = set()

        def is_tile_in_elem(tile_id, elem):
            tile_id, transform_mask = extract_transform_mask(tile_id)
            (_, _, elem_sprite_rect_width, _) = assets.sprite_rects[elem["image_id"]]
            elem_sprite_rect_cols = elem_sprite_rect_width // tileset.tile_size
            return (tile_id == elem["tile_id"] and not transform_mask
                or tile_id == elem["tile_id"] + elem_sprite_rect_cols - 1 and transform_mask == MASK_HORIZ)

        for (col, row), tile_id in layer.enumerate():
            if tile_id == -1:
                continue

            elem = next((e for e in elems if is_tile_in_elem(tile_id, e)), None)

            if not elem:
                if (col, row) not in visited_cells:
                    # draw tile onto surface
                    layer_data[(col, row)] = tile_id
                    tile_image = cls.resolve_tile_image_from_id(tile_id)
                    image.paste(
                        tile_image,
                        (col * tileset.tile_size, row * tileset.tile_size),
                        mask=tile_image
                    )
                continue

            elem_image = assets.sprites[elem["image_id"]]
            elem_cols = elem_image.get_width() // TILE_SIZE
            elem_rows = elem_image.get_height() // TILE_SIZE
            layer_elems.append([(col + elem_cols // 2, row + elem_rows), elem["name"]])

            visited_cells.update({
                (col + c, row + r) for r in range(elem_rows)
                    for c in range(elem_cols)})

        return image, layer_elems, layer_data
