from os import listdir
from os.path import isfile, join, splitext, basename
import re

def collect_imports(path, prefix="", exclude=[], root=False):
  imports = {}
  pattern = re.compile("class (\w+)\(\w+")
  prefix = [prefix] if prefix else []
  for item in listdir(join(path, *prefix)):
    if item[:2] == "__" or item in exclude: continue
    item_path = join(path, *prefix, item)
    if not isfile(item_path):
      for key, val in collect_imports(path=path, prefix=join(*prefix, item)).items():
        imports[key] = val
    elif prefix or root:
      name, _ = splitext(item)
      item_file = open(item_path, "r")
      item_contents = item_file.read()
      match = pattern.search(item_contents)
      if match:
        key = match.group(1)
        imports[key] = ".".join([basename(path), *prefix, name])
      item_file.close()
  return imports

def write_mapping(name, mapping):
  imports_buffer = ""
  body_buffer = f"\ndef resolve_{name}(key):\n"
  for key, path in mapping.items():
    imports_buffer += f"from {path} import {key}\n"
    body_buffer += f"  if key == \"{key}\": return {key}\n"
  output_file = open(f"src/resolve/{name}.py", "w")
  output_file.write(imports_buffer + body_buffer)
  output_file.close()

def build_items(items):
  write_mapping(name="item", mapping=items)

def build_skills(skills):
  write_mapping(name="skill", mapping=skills)

def build_chars(chars):
  write_mapping(name="char", mapping=chars)

def build_elems(elems):
  write_mapping(name="elem", mapping=elems)

def build_floors(floors):
  write_mapping(name="floor", mapping=floors)

def collect_tilesets(path):
  tilesets = []
  for f in listdir(path):
    if f.startswith("__"):
      continue
    hook_path = join(path, f)
    if isfile(hook_path):
      hook_key, _ = splitext(f)
    else:
      hook_key = f
    if "tiles" in listdir(hook_path):
      tilesets.append(hook_key)
  return tilesets

def build_tilesets(path):
  tilesets = collect_tilesets(path)
  imports_buffer = ""
  body_buffer = "\ndef resolve_tileset(key):\n"

  for key in tilesets:
    imports_buffer += f"import locations.{key}.tiles as {key}_tileset\n"
    body_buffer += f"  if key == \"{key}\": return {key}_tileset\n"

  output_file = open("src/resolve/tileset.py", "w")
  output_file.write(imports_buffer + body_buffer)
  output_file.close()

def collect_hooks(path):
  hooks = {}
  for f in listdir(path):
    if f.startswith("__"):
      continue
    hook_path = join(path, f)
    if isfile(hook_path):
      hook_key, _ = splitext(f)
      hook_file = open(hook_path, "r")
      hook_body = hook_file.read()
      hook_file.close()
      hooks[hook_key] = hook_body
    else:
      hooks[f] = collect_hooks(join(path, f))
  return hooks

def build_hooks(path):
  hooks = collect_hooks(path)
  imports_buffer = ""
  body_buffer = "\ndef resolve_hook(key):\n"
  pattern = re.compile("def (\w+)\(\w+")
  stack = [*hooks.items()]
  while stack:
    key, val = stack.pop()
    if type(val) is str:
      match = pattern.search(val)
      if not match:
        print(f"WARNING: Failed to match {key}")
        continue
      hook_name = match.group(1)
      hook_path = key
      hook_key = key.replace(".", "")
      imports_buffer += "from {import_path} import {hook_name} as {hook_key}\n".format(
        import_path=".".join(path.split("/")[1:] + [hook_path]),
        hook_name=hook_name,
        hook_key=hook_key
      )
      body_buffer += f"  if key == \"{hook_path}\": return {hook_key}\n"
    elif type(val) is dict:
      stack += [(key + "." + k, v) for k, v in val.items()]
  output_file = open(f"src/resolve/hook.py", "w")
  output_file.write(imports_buffer + body_buffer)
  output_file.close()

def collect_materials(materials_path, actors_path):
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

def build_materials(items, actors, materials):
  imports_buffer = ""
  body_buffer = "\ndef resolve_material(material):\n"

  for key, path in items.items():
    imports_buffer += f"from {path} import {key}\n"

  for key, path in actors.items():
    imports_buffer += f"from {path} import {key}\n"

  for material, enemy in materials.items():
    if material in items:
      body_buffer += f"  if material is {material}: return {enemy}\n"

  output_file = open("src/resolve/material.py", "w")
  output_file.write(imports_buffer + body_buffer)
  output_file.close()

if __name__ == "__main__":
  build_items(items=collect_imports("src/items"))
  build_skills(skills=collect_imports("src/skills"))
  build_chars(chars=collect_imports("src/cores", root=True))
  build_elems(elems=collect_imports("src/dungeon", exclude=["features", "floors", "gen"]))
  build_tilesets(path="src/locations")
  build_floors(floors=collect_imports("src/dungeon", prefix="floors"))
  build_hooks(path="src/dungeon/hooks")
  build_materials(
    items=collect_imports("src/items"),
    actors=collect_imports("src/dungeon", prefix="actors"),
    materials=collect_materials(
      materials_path="src/items/materials",
      actors_path="src/dungeon/actors"
    )
  )
