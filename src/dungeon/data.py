from json import JSONEncoder
from types import FunctionType
from dataclasses import dataclass
from dungeon.element import DungeonElement
from dungeon.stage import Stage, Tile
from dungeon.decor import Decor
from dungeon.features.room import Room
from savedata.resolve import resolve_elem, resolve_item, resolve_skill

@dataclass
class DungeonData:
  floors: list[Stage]
  floor_index: int
  memory: list[list[tuple[int, int]]]

  class Encoder(JSONEncoder):
    def default(encoder, obj):
      if type(obj) is type and issubclass(obj, Tile):
        return Stage.TILES.index(obj) if obj in Stage.TILES else -1
      if type(obj) in (DungeonData, Stage, Decor):
        return obj.__dict__
      if isinstance(obj, DungeonElement):
        return obj.encode()
      if isinstance(obj, Room):
        return ((*obj.cell, *obj.size), type(obj).__name__)
      if isinstance(obj, FunctionType):
        return obj.__name__
      return JSONEncoder.default(encoder, obj)

  def decode_floor(floor_data):
    floor = Stage(
      size=floor_data["size"],
      data=[Stage.TILES[t] for t in floor_data["data"]]
    )

    floor.entrance = floor_data["entrance"] or floor.find_tile(Stage.STAIRS_DOWN)
    floor.rooms = [Room((width, height), (x, y)) for (x, y, width, height), room_type in floor_data["rooms"]]
    floor.decors = [
      Decor(**decor_data) for decor_data in [{
        **d,
        "cell": tuple(d["cell"]),
        "offset": tuple(d["offset"]),
        "color": tuple(d["color"])
      } for d in floor_data["decors"]]
    ]

    for elem_cell, elem_name, *elem_props in floor_data["elems"]:
      elem_props = elem_props[0] if elem_props else {}
      if "contents" in elem_props:
        elem_contents = elem_props["contents"]
        elem_props["contents"] = resolve_item(elem_contents) or resolve_skill(elem_contents)
      elem = resolve_elem(elem_name)(**elem_props)
      floor.spawn_elem_at(tuple(elem_cell), elem)

    return floor
