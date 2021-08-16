import json
from dataclasses import dataclass, field
from items import Item
from skills import Skill, get_skill_order
from cores import Core
from contexts import Context
from dungeon.data import DungeonData
from savedata import SaveData
from savedata.resolve import resolve_item, resolve_skill, resolve_core
from config import MAX_SP, KNIGHT_BUILD, MAGE_BUILD, ROGUE_BUILD

def decode_build(build_data):
  return [(resolve_skill(skill_name), skill_cell)
    for (skill_name, skill_cell) in build_data.items()]

@dataclass
class GameData:
  time: int = 0
  sp: int = 0
  gold: int = 0
  items: list[Item] = field(default_factory=lambda: [])
  skills: list[Skill] = field(default_factory=lambda: [])
  new_skills: list[Skill] = field(default_factory=lambda: [])
  selected_skill: dict[str, str] = field(default_factory=lambda: {})
  party: list[Core] = field(default_factory=lambda: [])
  builds: dict[str, dict] = field(default_factory=lambda: {})
  kills: dict[str, int] = field(default_factory=lambda: {})
  story: list[str] = field(default_factory=lambda: [])
  place: Context = None
  dungeon: DungeonData = None

  class Encoder(json.JSONEncoder):
    def default(encoder, obj):
      if type(obj) is DungeonData:
        return DungeonData.Encoder.default(encoder, obj)
      return json.JSONEncoder.default(encoder, obj)

  def encode(store):
    place = type(store.place).__name__.startswith("Town") and "town" or "dungeon"
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
      place=place,
      dungeon=(place == "dungeon" and store.place.save() or None)
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
      dungeon=(savedata.dungeon and DungeonData(**savedata.dungeon))
    )

  def regen_sp(store, amount=None):
    if amount is None:
      store.sp = store.sp_max
      return
    store.sp = min(store.sp_max, store.sp + amount)

  def deplete_sp(store, amount=None):
    if amount is None:
      store.sp = 0
      return
    store.sp = max(0, store.sp - amount)

  def obtain_item(store, item):
    if item in store.items:
      return False
    store.items.append(item)
    return True

  def discard_item(store, item):
    if item not in store.items:
      return False
    store.items.remove(item)
    return True

  def learn_skill(store, skill):
    if skill in store.skills:
      return False
    store.new_skills.append(skill)
    store.skills.append(skill)
    store.skills.sort(key=get_skill_order)
    return True

  def recruit(store, core):
    core.faction = "player"
    core_id = type(core).__name__
    store.builds[core_id] = decode_build(store.builds[core_id] if core_id in store.builds else {
      "Knight": KNIGHT_BUILD,
      "Mage": MAGE_BUILD,
      "Rogue": ROGUE_BUILD,
    }[core_id])
    if len(store.party) == 1:
      store.party.append(core)
    else:
      store.party[1] = core

  def switch_chars(store):
    store.party.append(store.party.pop(0))
