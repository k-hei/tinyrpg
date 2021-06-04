from os import listdir
from os.path import isfile, join, splitext, basename
import re

def build_tree(path, prefix=[], root=False):
  imports = {}
  pattern = re.compile("class (\w+)\(\w+\)")
  for item in listdir(join(path, *prefix)):
    if item[:2] == "__": continue
    item_path = join(path, *prefix, item)
    if not isfile(item_path):
      for key, val in build_tree(path, prefix + [item]).items():
        imports[key] = val
    elif prefix or root:
      name, ext = splitext(item)
      item_file = open(item_path, "r")
      item_contents = item_file.read()
      match = pattern.search(item_contents)
      if match:
        key = match.group(1)
        imports[key] = ".".join([basename(path), *prefix, name])
      item_file.close()
  return imports

def build_materials(materials_path, actors_path):
  materials = {}
  pattern = re.compile("class (\w+)\(\w+\):")
  for item in listdir(materials_path):
    if item[:2] == "__": continue
    item_path = join(materials_path, item)
    item_file = open(item_path, "r")
    item_contents = item_file.read()
    match = pattern.search(item_contents)
    if match:
      key = match.group(1)
      materials[key] = None
    item_file.close()

  pattern = re.compile("class (\w+)\(\w+\):(?:\n|.)+drops = \[(\w+)")
  for item in listdir(actors_path):
    if item[:2] == "__": continue
    item_path = join(actors_path, item)
    item_file = open(item_path, "r")
    item_contents = item_file.read()
    match = pattern.search(item_contents)
    if match:
      enemy = match.group(1)
      drop = match.group(2)
      if enemy and drop:
        materials[drop] = enemy
    item_file.close()

  return materials

def build_buffer(items, skills, actors, materials):
  buffer = ""
  for key, path in items.items():
    buffer += "from {} import {}\n".format(path, key)
  for key, path in skills.items():
    buffer += "from {} import {}\n".format(path, key)
  for key, path in actors.items():
    buffer += "from dungeon.{} import {}\n".format(path, key)

  buffer += "\ndef resolve_item(key):\n"
  for key, path in items.items():
    buffer += "  if key == \"{}\": return {}\n".format(key, key)

  buffer += "\ndef resolve_skill(key):\n"
  for key, path in skills.items():
    buffer += "  if key == \"{}\": return {}\n".format(key, key)

  buffer += "\ndef resolve_material(material):\n"
  for material, enemy in materials.items():
    buffer += "  if material is {}: return {}\n".format(material, enemy)

  return buffer

if __name__ == "__main__":
  items = build_tree("src/items")
  skills = build_tree("src/skills")
  actors = build_tree("src/dungeon/actors", root=True)
  materials = build_materials("src/items/materials", "src/dungeon/actors")
  buffer = build_buffer(items, skills, actors, materials)
  print(buffer)
  output_file = open("src/savedata/resolve.py", "w")
  output_file.write(buffer)
  output_file.close()
