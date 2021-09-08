import debug
import json
from dataclasses import dataclass, field
from items import Item
from items.gold import Gold
from inventory import Inventory
from skills import Skill, get_skill_order
from cores import Core
from contexts import Context
from dungeon.data import DungeonData
from savedata import SaveData
from savedata.resolve import resolve_item, resolve_skill, resolve_elem, resolve_core
from config import (
  MAX_SP,
  INVENTORY_COLS, INVENTORY_ROWS,
  KNIGHT_BUILD, MAGE_BUILD, ROGUE_BUILD
)

def decode_build(build_data):
  if type(build_data) is dict:
    build_data = list(build_data.items())
  if not build_data:
    return {}
  if type(build_data[0][0]) is str:
    return [(resolve_skill(skill_name), skill_cell)
      for skill_name, skill_cell in build_data]
  else:
    return build_data

@dataclass
class GameData:
  time: int = 0
  _sp: int = 0
  sp_max: int = MAX_SP
  gold: int = 0
  items: list[Item] = field(default_factory=lambda: [])
  skills: list[Skill] = field(default_factory=lambda: [])
  new_skills: list[Skill] = field(default_factory=lambda: [])
  selected_skill: dict[str, str] = field(default_factory=lambda: {})
  party: list[Core] = field(default_factory=lambda: [])
  builds: dict[str, dict] = field(default_factory=lambda: {})
  kills: dict[str, int] = field(default_factory=lambda: {})
  story: list[str] = field(default_factory=lambda: [])
  quests: dict[str, bool] = field(default_factory=lambda: {})
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
      sp_max=store.sp_max,
      gold=store.gold,
      items=[i.__name__ for i in store.items],
      skills=[s.__name__ for s in store.skills],
      new_skills=[s.__name__ for s in store.new_skills],
      selected_skill={ n: s.__name__ for n, s in store.selected_skill.items() if s is not None },
      party=[type(c).__name__ for c in store.party],
      builds=builds,
      kills={ enemy.__name__: kills for enemy, kills in store.kills.items() },
      story=store.story,
      quests=store.quests,
      place=place,
      dungeon=(store.place.save()
        if store.place and place == "dungeon"
        else None)
    )

  def decode(savedata):
    party = [resolve_core(n)(faction="player") for n in savedata.party]
    builds = {}
    for name, build in savedata.builds.items():
      builds[name] = []
      for skill, cell in build.items():
        piece = (resolve_skill(skill), cell)
        builds[name].append(piece)
    return GameData(
      time=savedata.time,
      _sp=savedata.sp,
      sp_max=savedata.sp_max,
      gold=savedata.gold,
      items=[resolve_item(i) for i in savedata.items],
      skills=[resolve_skill(s) for s in savedata.skills],
      new_skills=[resolve_skill(s) for s in savedata.new_skills],
      selected_skill={ n: resolve_skill(s) for n, s in savedata.selected_skill.items() },
      party=party,
      builds=builds,
      kills={ resolve_elem(name): kills for name, kills in savedata.kills.items() },
      story=savedata.story,
      quests=savedata.quests,
      place=savedata.place,
      dungeon=(DungeonData(**savedata.dungeon)
        if savedata.dungeon and type(savedata.dungeon) is not DungeonData
        else savedata.dungeon)
    )

  @property
  def sp(store):
    return store._sp

  @sp.setter
  def sp(store, sp):
    store._sp = max(0, min(store.sp_max, sp))

  def obtain(store, target):
    if isinstance(target, Item) or issubclass(target, Item):
      return store.obtain_item(item=target)
    elif issubclass(target, Skill):
      return store.learn_skill(skill=target)
    else:
      debug.log("Failed to obtain unrecognized item {}".format(target))
      return False

  def obtain_item(store, item):
    if type(item) is Gold:
      store.gold += item.amount
      return True
    return Inventory.append(store.items, item)

  def use_item(store, item):
    success, message = item().use(store)
    if success:
      store.items.remove(item)
    return success, message

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
    print(store.builds)
    if len(store.party) == 1:
      store.party.append(core)
    else:
      store.party[1] = core

  def switch_chars(store):
    store.party.append(store.party.pop(0))

  def is_quest_accepted(store, quest):
    return quest in store.quests and store.quests[quest] == False

  def is_quest_completed(store, quest):
    return quest in store.quests and store.quests[quest] == True

  def accept_quest(store, quest):
    store.quests[quest] = False

  def complete_quest(store, quest):
    store.quests[quest] = True
