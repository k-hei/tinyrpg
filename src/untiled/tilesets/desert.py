from PIL import Image
from untiled import TilesetProcessor
from untiled.tileset import Tileset
from untiled.transform import transform_image, extract_transform_mask


tileset = Tileset(
    size=16,
    image=Image.open("assets/desert-tiles.png")
)


class DesertProcessor(TilesetProcessor):

    @classmethod
    def process(cls, layer, image=None):
        layer_width, layer_height = cls.get_layer_dimensions(layer) # TODO: layer class
        layer_image = image or Image.new(
            mode="RGBA",
            size=(layer_width * tileset.tile_size, layer_height * tileset.tile_size)
        )

        for row in range(layer_height):
            for col in range(layer_width):
                tile_id = layer[row][col]
                if tile_id == -1:
                    continue

                tile_id, transform_mask = extract_transform_mask(tile_id)
                tile_image = tileset.get(tile_id)
                tile_image = transform_image(tile_image, transform_mask)
                layer_image.paste(
                    tile_image,
                    (col * tileset.tile_size, row * tileset.tile_size),
                    mask=tile_image
                )

        return layer_image
