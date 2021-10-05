import json
import os
from dataclasses import dataclass
from dungeon.data import DungeonData
import debug

@dataclass
class SaveData:
  time: int
  sp: int
  sp_max: int
  gold: int
  items: list[str]
  skills: list[str]
  new_skills: list[str]
  selected_skill: dict[str, str]
  party: list[str]
  builds: dict[str, dict]
  kills: dict[str, int]
  story: list[str]
  quests: dict[str, bool]
  place: str
  dungeon: dict[str, dict] = None
  controls: dict[str, str] = None

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
