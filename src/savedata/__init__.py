import json
import os
from dataclasses import dataclass
from items import Item
from skills import Skill

@dataclass
class SaveData:
  sp: int
  time: int
  gold: int
  items: list[Item]
  skills: list[Skill]
  party: list[str]
  chars: dict[str, dict]
  place: str
  dungeon: dict[str, dict] = None

def load(*paths):
  try:
    data = {}
    for path in paths:
      savefile = open(path, "r")
      data.update(**json.loads(savefile.read()))
      savefile.close()
  except OSError:
    return None
  return SaveData(**data)

def save(path, data):
  savefile = open(path, "w")
  savefile.write(json.dumps(data))
  savefile.close()

def delete(path):
  os.remove(path)
