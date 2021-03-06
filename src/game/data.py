import debug
import json
from dataclasses import dataclass, field
from items import Item
from items.gold import Gold
from items.equipment import EquipmentItem
from inventory import Inventory
from skills import Skill, get_skill_order
from skills.weapon import Weapon
from cores import Core
from contexts import Context
from dungeon.data import DungeonData
from savedata import SaveData
from game.controls import ControlPreset
from resolve.item import resolve_item
from resolve.skill import resolve_skill
from resolve.elem import resolve_elem
from resolve.char import resolve_char
from config import (
  MAX_SP,
  INVENTORY_COLS, INVENTORY_ROWS,
  KNIGHT_BUILD, MAGE_BUILD, ROGUE_BUILD
)

def decode_build(build_data):
  if type(build_data) is dict:
    build_data = list(build_data.items())
  if not build_data:
    return []
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
  controls: ControlPreset = None

  class Encoder(json.JSONEncoder):
    def default(encoder, obj):
      if type(obj) is DungeonData:
        return DungeonData.Encoder.default(encoder, obj)
      return json.JSONEncoder.default(encoder, obj)

  def encode(store):
    place = ("town" if type(store.place).__name__.startswith("Town")
      else "dungeon" if not store.place.stage.is_overworld
      else None)
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
        else None),
      controls=store.controls and store.controls.__dict__
    )

  def decode(savedata):
    party = [resolve_char(n)(faction="player") for n in savedata.party]
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
        else savedata.dungeon),
      controls=savedata.controls and ControlPreset(**savedata.controls),
    )

  @property
  def sp(store):
    return store._sp

  @sp.setter
  def sp(store, sp):
    store._sp = max(0, min(store.sp_max, sp))

  @property
  def hero(store):
    return store.party[0] if len(store.party) >= 1 else None

  @property
  def ally(store):
    return store.party[1] if len(store.party) >= 2 else None

  def restore_party(store):
    store.sp = store.sp_max
    for core in store.party:
      core.heal()

  def obtain(store, target):
    if isinstance(target, Item) or type(target) is type and issubclass(target, Item):
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
    if type(item) is EquipmentItem or type(item) is type and issubclass(item, EquipmentItem):
      return store.learn_skill(skill=item.skill)
    return Inventory.append(store.items, item)

  def use_item(store, item, discard=True):
    success, message = item().use(store)
    if success is not False and discard:
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

  def forget_skill(store, skill):
    if skill not in store.skills:
      return False

    store.skills.remove(skill)

    if skill in store.new_skills:
      store.new_skills.remove(skill)

    store.unequip_skill(skill)
    return True

  def unequip_skill(store, skill, actor=None):
    if actor is None:
      for actor in store.builds.keys():
        store.unequip_skill(skill, actor)
      return

    build = store.builds[actor]
    piece = next(((s, c) for s, c in build if s is skill), None)
    if piece:
      build.remove(piece)

  def load_build(store, actor, build=None):
    if build:
      store.builds[type(actor).__name__] = build
    else:
      build = store.builds[type(actor).__name__]

    actor.skills = sorted([skill for skill, cell in build], key=get_skill_order)
    active_skills = actor.get_active_skills()
    store.set_selected_skill(actor, skill=next((s for s in active_skills if not issubclass(s, Weapon)), None))

  def update_skills(store):
    for core in store.party:
      core_id = type(core).__name__
      store.load_build(actor=core, build=store.builds[core_id] if core_id in store.builds else [])

  def get_selected_skill(store, core):
    core_id = type(core).__name__
    return (
      store.selected_skill[core_id]
        if core_id in store.selected_skill
        else None
    )

  def set_selected_skill(store, core, skill):
    core_id = type(core).__name__
    store.selected_skill[core_id] = skill

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

  def is_quest_accepted(store, quest):
    return quest in store.quests and store.quests[quest] is False

  def is_quest_completed(store, quest):
    return quest in store.quests and store.quests[quest] is True

  def accept_quest(store, quest):
    store.quests[quest] = False

  def complete_quest(store, quest):
    store.quests[quest] = True
