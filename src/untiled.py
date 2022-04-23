"""
Entry point for Tiled output conversion.
"""

import sys
import json
from enum import Enum, auto
from dataclasses import dataclass, field
from os.path import basename, splitext
from untiled import decode
from untiled.tilesets.desert import DesertProcessor


class LayerType(Enum):
    """
    Enumerates different layer types.
    """
    TILE = auto()
    OBJECT = auto()
    TRIGGER = auto()


@dataclass
class LayerProcessingRequest:
    """
    A persistent namespace that accumulates data between layers.
    """
    image: any = None
    tiles: any = field(default_factory=list)  # tile layers
    elems: any = field(default_factory=list)
    rooms: any = field(default_factory=list)


def process_tile_layer(processor, request, layer):
    """
    Handles processing tile layers.
    """
    request.image = processor.process_tile_layer(
        layer=layer,
        image=request.image,
    )
    request.tiles.append(layer.data)

def process_object_layer(processor, request, layer):
    """
    Handles processing object layers.
    """
    layer_image, layer_elems, layer_tiles = processor.process_object_layer(
        layer=layer,
        image=request.image,
    )
    request.image = layer_image
    request.tiles.append(layer_tiles.data)  # add new layer
    request.elems += layer_elems

def process_trigger_layer(processor, request, layer):
    """
    Handles processing trigger layers.
    """
    layer_image, layer_rooms = processor.process_trigger_layer(
        layer=layer,
        image=request.image,
    )
    request.image = layer_image
    request.rooms += layer_rooms


LAYER_TYPE_HANDLER_MAP = {
    LayerType.TILE: process_tile_layer,
    LayerType.OBJECT: process_object_layer,
    LayerType.TRIGGER: process_trigger_layer,
}


def process_layer(processor, request, layer, layer_type):
    """
    Handles layer type -> handler disambiguation.
    """

    handle_layer = LAYER_TYPE_HANDLER_MAP[layer_type]
    handle_layer(processor, request, layer)

def process_layers(processor, layers):
    """
    Processes layers using the given processor.
    """
    request = LayerProcessingRequest()
    for layer_type, layer in layers:
        process_layer(processor, request, layer, layer_type)

    return request.image, request.tiles, request.elems, request.rooms


def main():
    """
    Reads Tiled data from a file and translates it
    into a room directly compatible with the game engine.
    """

    argc = len(sys.argv)
    if argc != 2:
        print("usage: untiled.py pzlt1.json")
        exit()

    input_path = sys.argv[1]
    with open(input_path, mode="r", encoding="utf-8") as file:
        room_buffer = file.read()
        room_data = json.loads(room_buffer)

    layers = decode(**room_data)

    input_filename = basename(input_path)
    output_dir = input_path[:-len(input_filename)]
    room_name, _ = splitext(input_filename)
    output_filename = f"{room_name}_parsed.json"
    output_path = f"{output_dir}/{output_filename}"

    layer_image, layer_tiles, layer_elems, layer_rooms = process_layers(DesertProcessor, [
        (LayerType.TILE, layers["bp1"]),
        (LayerType.OBJECT, layers["bp2"]),
        (LayerType.OBJECT, layers["front1"]),
        (LayerType.OBJECT, layers["front2"]),
        (LayerType.OBJECT, layers["front3"]),
        (LayerType.TRIGGER, layers["obj"]),
    ])

    layer_image.save(f"{output_dir}/{room_name}.png")
    output_buffer = json.dumps({
        "bg": ("tileset", "desert"),
        "size": layers["bp1"].size,
        "tiles": layer_tiles,
        "elems": layer_elems,
        "rooms": layer_rooms,
        "edges": [(26, 2)],  # TODO: un-hardcode this
    }, separators=(",", ":"))

    output_path = f"rooms/{input_filename}"
    with open(output_path, mode="w", encoding="utf-8") as file:
        file.write(output_buffer)

    # room_file = open("rooms/" + room_path, "w")
    # with open("rooms/" + room_path, "w")
    # room_file.write(json.dumps(layers_data))

if __name__ == "__main__":
    main()
