import pygame
import keyboard
from config import WINDOW_SIZE, DEBUG
from contexts import Context
from contexts.pause import PauseContext
from dungeon.context import DungeonContext
from town import TownContext
from transits.dissolve import DissolveIn, DissolveOut
from cores.knight import KnightCore
from cores.mage import MageCore
from cores.rogue import RogueCore
from inventory import Inventory
from skills import get_skill_order
from savedata import SaveData
from savedata.resolve import resolve_item, resolve_skill

def resolve_place(place):
  if place == "dungeon": return DungeonContext()
  if place == "town": return TownContext()

def resolve_char(char):
  if char == "knight": return KnightCore()
  if char == "mage": return MageCore()
  if char == "rogue": return RogueCore()

def encode_char(char):
  if type(char) is KnightCore: return "knight"
  if type(char) is MageCore: return "mage"
  if type(char) is RogueCore: return "rogue"

class GameContext(Context):
  def __init__(ctx, savedata):
    super().__init__()
    ctx.savedata = savedata
    ctx.transits = [DissolveOut(WINDOW_SIZE)] if not DEBUG else []
    ctx.hero = None
    ctx.ally = None
    ctx.gold = 0
    ctx.sp_max = 40
    ctx.sp = ctx.sp_max
    ctx.time = 0
    ctx.inventory = Inventory((2, 4))
    ctx.monster_kills = {}
    ctx.new_skills = []
    ctx.skill_pool = []
    ctx.skill_builds = {}
    ctx.selected_skills = {}
    ctx.seeds = []
    ctx.debug = False

  def init(ctx):
    ctx.load()

  def load(ctx, savedata=None):
    if savedata is None:
      savedata = ctx.savedata

    ctx.sp = savedata.sp
    ctx.time = savedata.time
    ctx.gold = savedata.gold
    ctx.inventory.items = list(map(resolve_item, savedata.items))
    ctx.skill_pool = list(map(resolve_skill, savedata.skills))

    hero, ally = savedata.party[0], None
    if len(savedata.party) == 2:
      hero, ally = savedata.party
    ctx.hero = resolve_char(hero)
    ctx.ally = resolve_char(ally)

    hero_data = savedata.chars[hero]
    ctx.skill_builds[ctx.hero] = []
    for skill, cell in hero_data.items():
      piece = (resolve_skill(skill), cell)
      ctx.skill_builds[ctx.hero].append(piece)

    if ctx.ally:
      ally_data = savedata.chars[ally]
      ctx.skill_builds[ctx.ally] = []
      for skill, cell in ally_data.items():
        piece = (resolve_skill(skill), cell)
        ctx.skill_builds[ctx.ally].append(piece)

    ctx.open(resolve_place(savedata.place))

  def save(ctx):
    encode = lambda x: type(x).__name__
    items = list(map(encode, ctx.inventory.items))
    skills = list(map(encode, ctx.skill_pool))
    party = [encode_char(ctx.hero)]
    if ctx.ally:
      party.append(encode_char(ctx.ally))
    chars = {}
    for char, pieces in ctx.skill_builds.items():
      build = {}
      for skill, cell in pieces:
        build[encode(skill)] = list(cell)
      chars[encode_char(char)] = build
    return SaveData(
      place="town",
      sp=ctx.sp,
      time=int(ctx.time),
      gold=ctx.gold,
      items=items,
      skills=skills,
      party=party,
      chars=chars
    )

  def reset(ctx):
    if type(ctx.child) is DungeonContext:
      ctx.goto_dungeon()
    elif type(ctx.child) is TownContext:
      ctx.goto_town()

  def goto_dungeon(ctx):
    ctx.open(DungeonContext())

  def goto_town(ctx, returning=False):
    ctx.open(TownContext(returning=returning))

  def record_kill(ctx, target):
    target_type = type(target)
    if target_type in ctx.monster_kills:
      ctx.monster_kills[target_type] += 1
    else:
      ctx.monster_kills[target_type] = 1

  def get_skill(ctx, actor):
    return ctx.selected_skills[actor]

  def set_skill(ctx, actor, skill):
    ctx.selected_skills[actor] = skill

  def learn_skill(ctx, skill):
    if not skill in ctx.skill_pool:
      ctx.new_skills.append(skill)
      ctx.skill_pool.append(skill)
      ctx.skill_pool.sort(key=get_skill_order)

  def load_build(ctx, actor, build):
    ctx.skill_builds[actor] = build
    actor.skills = [skill for skill, cell in build]
    active_skills = actor.get_active_skills()
    ctx.set_skill(actor, active_skills[0] if active_skills else None)

  def update_skills(ctx):
    ctx.load_build(ctx.hero, ctx.skill_builds[ctx.hero])
    if ctx.ally:
      ctx.load_build(ctx.ally, ctx.skill_builds[ctx.ally])

  def get_gold(ctx):
    return ctx.gold

  def change_gold(ctx, amount):
    ctx.gold += amount

  def get_sp(ctx):
    return ctx.sp

  def get_sp_max(ctx):
    return ctx.sp_max

  def regen_sp(ctx, amount=None):
    if amount is None:
      ctx.sp = ctx.sp_max
      return
    ctx.sp = min(ctx.sp_max, ctx.sp + amount)

  def deplete_sp(ctx, amount=None):
    if amount is None:
      ctx.sp = 0
      return
    ctx.sp = max(0, ctx.sp - amount)

  def dissolve(ctx, on_clear, on_end=None):
    ctx.transits.append(DissolveIn(WINDOW_SIZE, on_clear))
    ctx.transits.append(DissolveOut(WINDOW_SIZE, on_end))

  def handle_keydown(ctx, key):
    if ctx.transits:
      return False
    if super().handle_keydown(key) != None:
      return
    if keyboard.get_pressed(key) == 1 and not ctx.child.child:
      if key == pygame.K_ESCAPE:
        return ctx.handle_pause()

  def handle_pause(ctx):
    ctx.child.log.exit()
    ctx.child.open(PauseContext())

  def update(ctx):
    super().update()
    ctx.time += 1 / ctx.get_root().fps

  def draw(ctx, surface):
    super().draw(surface)
    if ctx.transits:
      transit = ctx.transits[0]
      transit.update()
      transit.draw(surface)
      if transit.done:
        ctx.transits.remove(transit)
