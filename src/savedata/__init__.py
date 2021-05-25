import json
import os
from dataclasses import dataclass
from items import Item
from skills import Skill

@dataclass
class SaveData:
  place: str
  sp: int
  time: int
  gold: int
  items: list[Item]
  skills: list[Skill]
  party: list[str]
  chars: dict[str, dict]

def load(path):
  try:
    savefile = open(path, "r")
    data = json.loads(savefile.read())
    return SaveData(**data)
  except OSError:
    return None

def save(path, data):
  savefile = open(path, "w")
  savefile.write(json.dumps(data))
  savefile.close()

def delete(path):
  os.remove(path)
