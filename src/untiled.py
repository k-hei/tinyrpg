import sys
import json
from os.path import basename, splitext
from untiled import decode
from untiled.tilesets.desert import DesertProcessor

from enum import Enum, auto


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


class LayerType(Enum):
    TILE = auto()
    OBJECT = auto()


def process_layers(processor, layers):
    """
    Processes layers using the given processor.
    """
    layer_image = None
    layer_elems = []
    layer_data = []
    for layer_type, layer in layers:
        if layer_type == LayerType.TILE:
            layer_image = processor.process_tile_layer(
                layer=layer,
                image=layer_image,
            )
            layer_data.append(layer.data)
        elif layer_type == LayerType.OBJECT:
            layer_image, elems, data = processor.process_object_layer(
                layer=layer,
                image=layer_image,
            )
            layer_elems += elems
            layer_data.append(data.data)

    return layer_image, layer_elems, layer_data

layer_image, layer_elems, layer_data = process_layers(DesertProcessor, [
    (LayerType.TILE, layers["bp1"]),
    (LayerType.OBJECT, layers["bp2"]),
    (LayerType.OBJECT, layers["front1"]),
    (LayerType.OBJECT, layers["front2"]),
    (LayerType.OBJECT, layers["front3"]),
])

layer_image.save(f"{output_dir}/{room_name}.png")
output_buffer = json.dumps({
    "bg": ("tileset", "desert"),
    "size": layers["bp1"].size,
    "tiles": layer_data,
    "elems": layer_elems,
    "edges": [(26, 2)],  # TODO: un-hardcode this
}, separators=(",", ":"))

output_path = f"rooms/{input_filename}"
with open(output_path, mode="w", encoding="utf-8") as file:
    file.write(output_buffer)

# room_file = open("rooms/" + room_path, "w")
# with open("rooms/" + room_path, "w")
# room_file.write(json.dumps(layers_data))
