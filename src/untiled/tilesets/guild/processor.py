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
    room_size = None
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
            room_bg_image = cls.load_image(image_layer["image"])
            cls.room_size = (
                room_bg_image.width // cls.tile_width,
                room_bg_image.height // cls.tile_height
            )
            cls.layer_offset = (image_layer["offsetx"], image_layer["offsety"])

    @classmethod
    def load_room_tilesets(cls, room):
        object_image_filenames = []
        for tileset in room["tilesets"]:
            tileset_path = join(cls.cwd, tileset["source"])
            object_image_filenames += [p for p in parse_tsx_from_path(tileset_path)]

        for object_image_filename in object_image_filenames:
            object_image = cls.load_image(object_image_filename)
            object_image.save(join("assets", "guild_" + object_image_filename))

        object_image_ids = [splitext(f)[0] for f in object_image_filenames]
        cls.object_image_ids = {i + 1: image_id for i, image_id in enumerate(object_image_ids)}

        object_images = [cls.load_image(f) for f in object_image_filenames]
        cls.object_images = {i + 1: image for i, image in enumerate(object_images)}

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

            elem_cell = (
                (obj_pos[0] + obj_image.width // 2) // cls.tile_width - 1,
                (obj_pos[1] + obj_image.height) // cls.tile_height
            )

            elems.append((elem_cell, elem_name))

        obj_sprites.sort(key=lambda sprite: sprite[1][1])
        for obj_image, obj_pos in obj_sprites:
            image.paste(obj_image, obj_pos, mask=obj_image)

        print(elems)
        return image, elems, []