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
  party: list[str]
  builds: dict[str, dict]
  story: list[str]
  place: str
  dungeon: DungeonData = None

  class Encoder(json.JSONEncoder):
    def default(encoder, obj):
      if type(obj) is DungeonData:
        return DungeonData.Encoder.default(encoder, obj)
      return json.JSONEncoder.default(encoder, obj)

  def encode(state, place):
    builds = {}
    for char, pieces in state.builds.items():
      build = {}
      for skill, cell in pieces:
        build[skill.__name__] = list(cell)
      builds[char.__name__.lower()] = build
    return SaveData(
      time=int(state.time),
      sp=state.sp,
      gold=state.gold,
      items=[i.__name__ for i in state.items],
      skills=[s.__name__ for s in state.skills],
      party=[c.__name__.lower() for c in state.party],
      builds=builds,
      story=state.story,
      place=state.place,
      dungeon=(state.place == "dungeon" and place.save() or None)
    )

  def decode(savedata):
    party = [resolve_core(n)() for n in savedata.party]
    builds = {}
    for name, build in savedata.builds.items():
      core = resolve_core(name)
      builds[core] = []
      for skill, cell in build.items():
        piece = (resolve_skill(skill), cell)
        builds[core].append(piece)
    return GameData(
      time=savedata.time,
      sp=savedata.sp,
      gold=savedata.gold,
      items=[resolve_item(i) for i in savedata.items],
      skills=[resolve_skill(s) for s in savedata.skills],
      party=party,
      builds=builds,
      story=savedata.story,
      place=savedata.place,
      dungeon=(savedata.place == "dungeon" and DungeonData(**savedata.dungeon) or None)
    )
