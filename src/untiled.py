"""
Entry point for Tiled output conversion.
"""

import sys
import json
from enum import Enum
from dataclasses import dataclass, field
from os.path import basename, splitext, dirname
from untiled.tilesets.resolver import resolve_processor


class LayerType(Enum):
    """
    Enumerates different layer types.
    """
    IMAGE = "image"
    TILE = "tile"
    OBJECT = "object"
    TRIGGER = "trigger"


@dataclass
class LayerProcessingRequest:
    """
    A persistent namespace that accumulates data between layers.
    """
    image: any = None
    tiles: any = field(default_factory=list)  # tile layers
    elems: any = field(default_factory=list)
    rooms: any = field(default_factory=list)
    edges: any = field(default_factory=list)


def process_image_layer(processor, request, layer):
    """
    Handles processing image layers.
    """
    request.image = processor.process_image_layer(
        layer=layer,
        image=request.image
    )

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
    layer_tiles and request.tiles.append(layer_tiles.data)  # add new layer
    request.elems += layer_elems

def process_trigger_layer(processor, request, layer):
    """
    Handles processing trigger layers.
    """
    layer_image, layer_elems, layer_rooms, layer_edges = processor.process_trigger_layer(
        layer=layer,
        image=request.image,
    )
    request.image = layer_image
    request.elems += layer_elems
    request.rooms += layer_rooms
    request.edges += layer_edges


LAYER_TYPE_HANDLER_MAP = {
    LayerType.IMAGE: process_image_layer,
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

    return request.image, request.tiles, request.elems, request.rooms, request.edges


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

    input_filename = basename(input_path)
    room_name, _ = splitext(input_filename)
    input_dir = input_path[:-len(input_filename)]

    meta_path = f"{input_dir}/{room_name}.meta.json"
    try:
        with open(meta_path, mode="r", encoding="utf-8") as file:
            meta_buffer = file.read()
            metadata = json.loads(meta_buffer)
    except FileNotFoundError:
        metadata = {}

    # layers = decode(**room_data)  # decoding zstd tile data is exclusive to maps with tile layers
    metadata["cwd"] = dirname(meta_path)
    processor = resolve_processor(metadata["tileset"]
        if "tileset" in metadata
        else None)

    processor.load_metadata(metadata)
    processor.load_room(room_data)

    layers = [(
        LayerType(t),
        next((layer for layer in room_data["layers"]
            if layer["name"] == l), None)
    ) for l, t in metadata["layers"].items()]

    room_image, room_tiles, room_elems, room_subrooms, room_edges = process_layers(
        processor=processor,
        layers=layers,
    )

    output_dir = input_dir
    output_filename = f"{room_name}_parsed.json"
    output_path = f"{output_dir}/{output_filename}"

    room_image.save(f"{output_dir}/{room_name}.png")

    try:
        room_size = layers[0][1].size
    except AttributeError:
        room_size = None

    output_buffer = json.dumps({
        "name": metadata["name"],
        "bg": ("tileset", metadata["tileset"]),
        "size": room_size,
        "tiles": room_tiles,
        "elems": room_elems,
        "rooms": room_subrooms,
        "edges": room_edges,
        **({"hooks": metadata["hooks"]} if "hooks" in metadata else {}),
        **({"ports": metadata["ports"]} if "ports" in metadata else {}),
    }, separators=(",", ":"))

    output_path = f"rooms/{input_filename}"
    with open(output_path, mode="w", encoding="utf-8") as file:
        file.write(output_buffer)

    # room_file = open("rooms/" + room_path, "w")
    # with open("rooms/" + room_path, "w")
    # room_file.write(json.dumps(layers_data))

if __name__ == "__main__":
    main()
