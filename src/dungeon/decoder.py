from dungeon.stage import Stage
from dungeon.decor import Decor
from dungeon.features.specialroom import SpecialRoom
from dungeon.features.vertroom import VerticalRoom
from savedata.resolve import resolve_elem, resolve_item, resolve_skill
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
    RoomType = resolve_elem(room_kind)
    is_special = (isinstance(RoomType, SpecialRoom)
      or isinstance(RoomType, (SpecialRoom, VerticalRoom)))
    try:
      if is_special:
        floor.rooms.append(RoomType(cell=(x, y), placed=True, **room_props))
      else:
        floor.rooms.append(RoomType(size=size, cell=(x, y), placed=True, **room_props))
    except:
      debug.log("WARNING: Failed to resolve {} {} is_special_room:{}".format(room_kind, room_props, is_special))
      raise

  for elem_cell, elem_name, *elem_props in floor_data["elems"]:
    elem_props = elem_props[0] if elem_props else {}
    if "contents" in elem_props:
      elem_contents = elem_props["contents"]
      elem_props["contents"] = resolve_item(elem_contents) or resolve_skill(elem_contents)
    if "message" in elem_props:
      message_key = elem_props["message"]
      elem_props["message"] = next((s for s in resolve_elem(floor_data["generator"]).scripts if s[0] == message_key), None)
    if "charge_skill" in elem_props:
      elem_props["charge_skill"] = resolve_skill(elem_props["charge_skill"])
    try:
      elem = resolve_elem(elem_name)(**elem_props)
    except:
      debug.log("WARNING: Failed to resolve {} {}".format(elem_name, elem_props))
      raise
    floor.spawn_elem_at(tuple(elem_cell), elem)

  return floor
