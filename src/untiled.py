import sys
import json
from os.path import basename, splitext
from untiled import decode
from untiled.tilesets.desert import DesertProcessor

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

layer_image = DesertProcessor.process_tile_layer(layers["bp1"])
layer_elems = DesertProcessor.process_object_layer(layers["bp2"])
# layer_image = DesertProcessor.process_tile_layer(layers["front1"], image=layer_image)
# layer_image = DesertProcessor.process(layers["front2"], image=layer_image)
# layer_image = DesertProcessor.process(layers["front3"], image=layer_image)
layer_image.save(f"{output_dir}/{room_name}.png")

print(layer_elems)

output_buffer = json.dumps({
    "bg": ("tileset", "desert"),
    "size": layers["bp1"].size,
    "tiles": layers["bp1"].data,
    "elems": layer_elems,
    "edges": [(26, 2)],
}, separators=(",", ":"))

with open(output_path, mode="w", encoding="utf-8") as file:
    file.write(output_buffer)

# room_file = open("rooms/" + room_path, "w")
# with open("rooms/" + room_path, "w")
# room_file.write(json.dumps(layers_data))
