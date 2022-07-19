from os.path import join, splitext
from PIL import Image
import lib.vector as vector
from untiled.tilesets.processor import Processor
from untiled.parse_tsx import parse_tsx_from_path
from untiled.transform import transform_image, rotate_image, \
    extract_transform_mask, extract_rotation_offset

from untiled.tilesets.processor import load_json
from locations.guild.tiles import GuildTileset


class GuildProcessor(Processor):
    tile_width = 0
    tile_height = 0
    layer_offset = (0, 0)
    object_image_ids = []
    object_images = []
    elems = load_json(GuildTileset.elems_path)
    cwd = ""

    @classmethod
    def load_room(cls, room):
        cls.tile_width = room["tilewidth"]
        cls.tile_height = room["tileheight"]
        cls.load_room_tilesets(room)

        image_layer = next((l for l in room["layers"]
            if l["type"] == "imagelayer"), None)
        if image_layer:
            cls.layer_offset = (image_layer["offsetx"], image_layer["offsety"])

    @classmethod
    def load_room_tilesets(cls, room):
        object_image_ids = []
        for tileset in room["tilesets"]:
            tileset_path = join(cls.cwd, tileset["source"])
            object_image_ids += [p for p in parse_tsx_from_path(tileset_path)]

        cls.object_image_ids = {i + 1: splitext(image_id)[0]
            for i, image_id in enumerate(object_image_ids)}

        cls.object_images = {i + 1: cls.load_image(image_id)
            for i, image_id in enumerate(object_image_ids)}

    @classmethod
    def load_metadata(cls, metadata):
        cls.cwd = metadata["cwd"]

    @classmethod
    def load_image(cls, image_path):
        image_path = join(cls.cwd, image_path)
        return Image.open(image_path)

    @classmethod
    def process_image_layer(cls, layer, image):
        image = cls.load_image(layer["image"])
        return image

    @classmethod
    def process_object_layer(cls, layer, image):
        elems = []

        obj_sprites = []
        for obj in layer["objects"]:
            obj_id = obj["gid"]
            obj_id, transform_mask = extract_transform_mask(obj_id)
            obj_image = cls.object_images[obj_id]
            obj_image = transform_image(obj_image, transform_mask)

            obj_rotation = obj["rotation"]
            obj_image = rotate_image(obj_image, obj_rotation)
            obj_offset = extract_rotation_offset(obj_image, obj_rotation)

            obj_pos = vector.add(
                (obj["x"], obj["y"]),
                obj_offset,
                vector.negate(cls.layer_offset),
            )

            obj_sprites.append((obj_image, obj_pos))

            elem_name = next((e["name"] for e in cls.elems
                if e["image_id"] == "guild_" + cls.object_image_ids[obj_id]), None)
            elems.append((
                elem_name,
                (obj_pos[0] // cls.tile_width, obj_pos[1] // cls.tile_height),
            ))

        obj_sprites.sort(key=lambda sprite: sprite[1][1])
        for obj_image, obj_pos in obj_sprites:
            image.paste(obj_image, obj_pos, mask=obj_image)

        print(elems)
        return image, elems, []
