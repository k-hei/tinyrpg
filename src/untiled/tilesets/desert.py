import json
from PIL import Image
from untiled import TilesetProcessor
from untiled.tileset import Tileset
from untiled.transform import transform_image, extract_transform_mask
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
            elem = next((elem for elem in elems if elem["tile_id"] == tile_id), None)
            if not elem:
                continue
            elem_image = assets.sprites[elem["image_id"]]
            col += elem_image.get_width() // 2 // TILE_SIZE
            row += elem_image.get_height() // TILE_SIZE
            layer_elems.append([(col, row), elem["name"]])

        return layer_elems
