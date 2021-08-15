import json
import os
from dataclasses import dataclass
from items import Item
from skills import Skill
from dungeon.data import DungeonData

@dataclass
class SaveData:
  time: int
  sp: int
  gold: int
  items: list[Item]
  skills: list[Skill]
  party: list[str]
  builds: dict[str, dict]
  story: list[str]
  place: str
  dungeon: dict[str, dict] = None

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
  return SaveData(**data)

def save(path, data):
  savefile = open(path, "w")
  savefile.write(json.dumps(data, cls=DungeonData.Encoder))
  savefile.close()

def delete(path):
  os.remove(path)
