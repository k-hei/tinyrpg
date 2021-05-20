import json
from dataclasses import dataclass
from items import Item
from skills import Skill

@dataclass
class SaveData:
  place: str
  sp: int
  gold: int
  items: list[Item]
  skills: list[Skill]
  party: list[str]
  chars: dict[str, dict]

def load(path):
  try:
    data = json.loads(open(path, "r").read())
    return SaveData(**data)
  except OSError:
    print("Failed to load data at \"{}\"".format(path))
    return None

def save(path, data):
  pass
