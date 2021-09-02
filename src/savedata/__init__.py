import json
import os
from dataclasses import dataclass
from items import Item
from skills import Skill
from dungeon.data import DungeonData
import debug

@dataclass
class SaveData:
  time: int
  sp: int
  sp_max: int
  gold: int
  items: list[Item]
  skills: list[Skill]
  new_skills: list[Skill]
  selected_skill: dict[str, Skill]
  party: list[str]
  builds: dict[str, dict]
  kills: dict[str, int]
  story: list[str]
  quests: dict[str, bool]
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
  buffer = json.dumps(data, cls=DungeonData.Encoder)
  savefile = open(path, "w")
  savefile.write(buffer)
  savefile.close()

def delete(path):
  os.remove(path)
