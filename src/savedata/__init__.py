import json
import os
from dataclasses import dataclass
from items import Item
from skills import Skill
from dungeon.data import DungeonData

@dataclass
class GameState:
  sp: int
  time: int
  gold: int
  items: list[Item]
  skills: list[Skill]
  party: list[str]
  chars: dict[str, dict]
  place: str
  story: dict[str, bool]
  dungeon: dict[str, dict] = None

  class Encoder(json.JSONEncoder):
    def default(encoder, obj):
      if type(obj) is DungeonData:
        return DungeonData.Encoder.default(encoder, obj)
      return json.JSONEncoder.default(encoder, obj)

def load(*paths):
  try:
    data = {}
    for path in paths:
      savefile = open(path, "r")
      savefile_contents = savefile.read()
      data.update(**json.loads(savefile_contents))
      savefile.close()
  except OSError:
    return None
  return GameState(**data)

def save(path, data):
  savefile = open(path, "w")
  savefile.write(json.dumps(data, cls=DungeonData.Encoder))
  savefile.close()

def delete(path):
  os.remove(path)
