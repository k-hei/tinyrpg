import sys
import json
from os.path import basename, splitext
from untiled import decode
from untiled.desert import DesertProcessor

argc = len(sys.argv)
if argc != 2:
    print("usage: untiled.py pzlt1.json")
    exit()

input_path = sys.argv[1]
with open(input_path, mode="r", encoding="utf-8") as file:
    room_buffer = file.read()
    room_data = json.loads(room_buffer)

layers_data = decode(**room_data)

input_filename = basename(input_path)
output_dir = input_path[:-len(input_filename)]
room_name, _ = splitext(input_filename)
output_filename = f"{room_name}_parsed.json"
output_path = f"{output_dir}/{output_filename}"
output_buffer = json.dumps(layers_data)

DesertProcessor.process(layers_data[0])

with open(output_path, mode="w", encoding="utf-8") as file:
    file.write(output_buffer)

# room_file = open("rooms/" + room_path, "w")
# with open("rooms/" + room_path, "w")
# room_file.write(json.dumps(layers_data))
