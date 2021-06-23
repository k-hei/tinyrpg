import pygame
import keyboard
from config import WINDOW_SIZE, DEBUG
from contexts import Context
from contexts.pause import PauseContext
from dungeon.context import DungeonContext
from town import TownContext
from cores.knight import Knight
from cores.mage import Mage
from cores.rogue import Rogue
from inventory import Inventory
from skills import get_skill_order
from savedata import SaveData
from savedata.resolve import resolve_item, resolve_skill

def resolve_char(char):
  if char == "knight": return Knight()
  if char == "mage": return Mage()
  if char == "rogue": return Rogue()

def encode_char(char):
  if type(char) is Knight: return "knight"
  if type(char) is Mage: return "mage"
  if type(char) is Rogue: return "rogue"

class GameContext(Context):
  def __init__(ctx, savedata):
    super().__init__()
    ctx.savedata = savedata
    ctx.party = []
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
    ctx.party = [resolve_char(n) for n in savedata.party]
    for i, char in enumerate(ctx.party):
      char_name = savedata.party[i]
      char_data = savedata.chars[char_name]
      ctx.skill_builds[char] = []
      for skill, cell in char_data.items():
        piece = (resolve_skill(skill), cell)
        ctx.skill_builds[char].append(piece)
    ctx.update_skills()
    if savedata.place == "dungeon":
      ctx.goto_dungeon()
    elif savedata.place == "town":
      ctx.goto_town()

  def save(ctx):
    encode = lambda x: x.__name__
    items = list(map(encode, ctx.inventory.items))
    skills = list(map(encode, ctx.skill_pool))
    party = [encode_char(c) for c in ctx.party]
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

  def recruit(ctx, char):
    ctx.skill_builds[char] = {}
    if len(ctx.party) == 1:
      ctx.party.append(char)
    else:
      ctx.party[1] = char

  def reset(ctx):
    if type(ctx.child) is DungeonContext:
      ctx.goto_dungeon()
    elif type(ctx.child) is TownContext:
      ctx.goto_town()

  def goto_dungeon(ctx):
    ctx.open(DungeonContext())

  def goto_town(ctx, returning=False):
    ctx.open(TownContext(party=ctx.party))

  def obtain(ctx, item):
    ctx.inventory.items.append(item)

  def record_kill(ctx, target):
    target_type = type(target)
    if target_type in ctx.monster_kills:
      ctx.monster_kills[target_type] += 1
    else:
      ctx.monster_kills[target_type] = 1

  def get_skill(ctx, actor):
    return ctx.selected_skills[actor] if actor in ctx.selected_skills else None

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
    for core in ctx.party:
      ctx.load_build(core, ctx.skill_builds[core])

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

  def handle_keydown(ctx, key):
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
