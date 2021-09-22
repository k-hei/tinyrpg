import sys
import json
from os.path import basename
from untiled import decode

argc = len(sys.argv)
if argc != 2:
  print("usage: untiled.py pzlt1.json")
  exit()

room_path = sys.argv[1]
room_file = open(room_path, "r")
room_data = json.loads(room_file.read())
room_file.close()

room = decode(**room_data)
room_path = basename(room_path)
room_file = open(f"rooms/{room_path}", "w")
room_file.write(json.dumps(room.__dict__))
