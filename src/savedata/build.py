from os import listdir
from os.path import isfile, join, splitext, basename
import re

def build_tree(path, prefix=[]):
  imports = {}
  pattern = re.compile("class (\w+)\(\w+\):\n  name")
  for item in listdir(join(path, *prefix)):
    if item[:2] == "__": continue
    item_path = join(path, *prefix, item)
    if not isfile(item_path):
      for key, val in build_tree(path, prefix + [item]).items():
        imports[key] = val
    elif prefix:
      name, ext = splitext(item)
      item_file = open(item_path, "r")
      item_contents = item_file.read()
      match = pattern.search(item_contents)
      if match:
        key = match.group(1)
        imports[key] = ".".join([basename(path), *prefix, name])
      item_file.close()
  return imports

def build_buffer(items, skills):
  buffer = ""
  for key, path in items.items():
    buffer += "from {} import {}\n".format(path, key)
  for key, path in skills.items():
    buffer += "from {} import {}\n".format(path, key)

  buffer += "\ndef resolve_item(key):\n"
  for key, path in items.items():
    buffer += "  if key == \"{}\": return {}\n".format(key, key)
  buffer += "  return None\n"

  buffer += "\ndef resolve_skill(key):\n"
  for key, path in skills.items():
    buffer += "  if key == \"{}\": return {}\n".format(key, key)
  buffer += "  return None\n"
  return buffer

if __name__ == "__main__":
  items = build_tree("src/items")
  skills = build_tree("src/skills")
  buffer = build_buffer(items, skills)
  print(buffer)
  output_file = open("src/savedata/resolve.py", "w")
  output_file.write(buffer)
  output_file.close()
