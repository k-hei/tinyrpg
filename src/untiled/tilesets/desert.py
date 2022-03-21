from PIL import Image
from untiled import TilesetProcessor
from untiled.tileset import Tileset
from untiled.transform import transform_image, extract_transform_mask
from locations.desert.elems.bush import DesertBush


tileset = Tileset(
    size=16,
    image=Image.open("assets/desert-tiles.png")
)


objects = [DesertBush]


class DesertProcessor(TilesetProcessor):

    @staticmethod
    def process_layer(layer, image=None):
        layer_width, layer_height = layer.size
        layer_image = image or Image.new(
            mode="RGBA",
            size=(layer_width * tileset.tile_size, layer_height * tileset.tile_size)
        )
        return layer_image

    @staticmethod
    def process_tile_layer(layer, image=None):
        layer_image = DesertProcessor.process_layer(layer, image)

        for (col, row), tile_id in layer.enumerate():
            if tile_id == -1:
                continue

            tile_id, transform_mask = extract_transform_mask(tile_id)
            tile_image = tileset[tile_id]
            tile_image = transform_image(tile_image, transform_mask)
            layer_image.paste(
                tile_image,
                (col * tileset.tile_size, row * tileset.tile_size),
                mask=tile_image
            )

        return layer_image

    @staticmethod
    def process_object_layer(layer):
        layer_elems = []

        for (col, row), tile_id in layer.enumerate():
            obj = next((o for o in objects if o.tile_id == tile_id), None)
            if not obj:
                continue
            col += obj.size[0] // 2
            row += obj.size[1]
            cell = (col, row)
            layer_elems.append(obj(cell))

        return layer_elems
