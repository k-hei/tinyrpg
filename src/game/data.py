import json
from dataclasses import dataclass
from items import Item
from skills import Skill
from dungeon.data import DungeonData
from savedata import SaveData
from savedata.resolve import resolve_item, resolve_skill, resolve_core

@dataclass
class GameData:
  time: int
  sp: int
  gold: int
  items: list[Item]
  skills: list[Skill]
  new_skills: list[Skill]
  selected_skill: dict[str, str]
  party: list[str]
  builds: dict[str, dict]
  kills: dict[str, int]
  story: list[str]
  place: str
  dungeon: DungeonData = None

  class Encoder(json.JSONEncoder):
    def default(encoder, obj):
      if type(obj) is DungeonData:
        return DungeonData.Encoder.default(encoder, obj)
      return json.JSONEncoder.default(encoder, obj)

  def encode(store):
    builds = {}
    for char, pieces in store.builds.items():
      build = {}
      for skill, cell in pieces:
        build[skill.__name__] = list(cell)
      builds[char] = build
    return SaveData(
      time=int(store.time),
      sp=store.sp,
      gold=store.gold,
      items=[i.__name__ for i in store.items],
      skills=[s.__name__ for s in store.skills],
      new_skills=[s.__name__ for s in store.new_skills],
      selected_skill={ n: s.__name__ for n, s in store.selected_skill.items() },
      party=[type(c).__name__ for c in store.party],
      builds=builds,
      kills=store.kills,
      story=store.story,
      place=store.place,
      dungeon=(store.place == "dungeon" and place.save() or None)
    )

  def decode(savedata):
    party = [resolve_core(n)() for n in savedata.party]
    builds = {}
    for name, build in savedata.builds.items():
      builds[name] = []
      for skill, cell in build.items():
        piece = (resolve_skill(skill), cell)
        builds[name].append(piece)
    return GameData(
      time=savedata.time,
      sp=savedata.sp,
      gold=savedata.gold,
      items=[resolve_item(i) for i in savedata.items],
      skills=[resolve_skill(s) for s in savedata.skills],
      new_skills=[resolve_skill(s) for s in savedata.new_skills],
      selected_skill={ n: resolve_skill(s) for n, s in savedata.selected_skill.items() },
      party=party,
      builds=builds,
      kills=savedata.kills,
      story=savedata.story,
      place=savedata.place,
      dungeon=(savedata.place == "dungeon" and DungeonData(**savedata.dungeon) or None)
    )
