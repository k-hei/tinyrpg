from dungeon.stage import Stage
from dungeon.decor import Decor
from dungeon.features.room import Room
from resolve.elem import resolve_elem
from resolve.item import resolve_item
from resolve.skill import resolve_skill
from resolve.elem import resolve_elem
from resolve.hook import resolve_hook
import debug

def decode_floor(floor_data):
  floor = Stage(
    size=floor_data["size"],
    data=[Stage.TILES[t] for t in floor_data["data"]]
  )

  floor.entrance = floor_data["entrance"] if "entrance" in floor_data else floor.find_tile(Stage.STAIRS_DOWN)
  floor.exit = tuple(floor_data["exit"]) if "exit" in floor_data and floor_data["exit"] else None
  floor.generator = floor_data["generator"] if "generator" in floor_data else None

  if "decors" in floor_data:
    floor.decors = [
      Decor(**decor_data) for decor_data in [{
        **d,
        "cell": tuple(d["cell"]),
        "offset": tuple(d["offset"]),
        "color": tuple(d["color"])
      } for d in floor_data["decors"]]
    ]

  for (x, y, *size), room_kind, *room_props in floor_data["rooms"]:
    room_props = room_props[0] if room_props else {}
    RoomType = resolve_elem(room_kind) or Room
    try:
      floor.rooms.append(RoomType(size=size, cell=(x, y), placed=True, **room_props))
    except:
      debug.log(f"WARNING: Failed to resolve {room_kind} {room_props}")
      raise

  for elem_cell, elem_name, *elem_props in floor_data["elems"]:
    elem_props = elem_props[0] if elem_props else {}
    elem = decode_elem(elem_cell, elem_name, elem_props)
    floor.spawn_elem_at(tuple(elem_cell), elem)

  return floor

def decode_elem(elem_cell, elem_name, elem_props, tileset=None):
  if "contents" in elem_props and type(elem_props["contents"]) is str:
    elem_props["contents"] = (
      resolve_item(elem_props["contents"])
      or resolve_skill(elem_props["contents"])
      or resolve_elem(elem_props["contents"])
    )

  if "on_action" in elem_props and type(elem_props["on_action"]) is str:
    elem_props["on_action"] = resolve_hook(elem_props["on_action"])

  # if "message" in elem_props:
  #   message_key = elem_props["message"]
  #   elem_props["message"] = next((s for s in resolve_elem(floor_data["generator"]).scripts if s[0] == message_key), None)

  if "charge_skill" in elem_props:
    elem_props["charge_skill"] = resolve_skill(elem_props["charge_skill"])

  try:
    return tileset and tileset.resolve_elem(elem_name)(**elem_props)
  except (AttributeError, KeyError) as e:
    debug.log(f"WARNING: Failed to resolve {elem_name} in {tileset}")
    # raise e

  try:
    return resolve_elem(elem_name)(**elem_props)
  except Exception:
    debug.log(f"WARNING: Failed to resolve {elem_name} {elem_props}")
    raise
