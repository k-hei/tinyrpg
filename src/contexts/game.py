import pygame

from config import WINDOW_SIZE, DEBUG
from contexts import Context
from dungeon import DungeonContext
from town import TownContext
from contexts.pause import PauseContext
from transits.dissolve import DissolveIn, DissolveOut
import keyboard

from cores.knight import KnightCore as Knight
from cores.mage import MageCore as Mage

from inventory import Inventory
from items.hp.potion import Potion
from items.hp.ankh import Ankh
from items.hp.ruby import Ruby
from items.hp.elixir import Elixir
from items.sp.bread import Bread
from items.sp.fish import Fish
from items.sp.sapphire import Sapphire
from items.dungeon.emerald import Emerald
from items.dungeon.balloon import Balloon
from items.ailment.antidote import Antidote
from items.ailment.amethyst import Amethyst

from skills import get_skill_order
from skills.weapon import Weapon
from skills.weapon.stick import Stick
from skills.armor.hpup import HpUp
from skills.attack.blitzritter import Blitzritter
from skills.magic.ignis import Ignis
from skills.support.counter import Counter
from skills.support.sana import Sana
from skills.ailment.somnus import Somnus

class GameContext(Context):
  def __init__(ctx, start_in_dungeon=False):
    super().__init__()
    ctx.transits = [DissolveOut(WINDOW_SIZE)] if not DEBUG else []
    ctx.inventory = Inventory((2, 4), [
      Ruby(), Sapphire(),
      Emerald(), Amethyst()
    ])
    ctx.sp_max = 50
    ctx.sp = ctx.sp_max // 2
    ctx.gold = 500
    ctx.hero = Knight()
    ctx.ally = Mage()
    ctx.new_skills = []
    ctx.skill_pool = [
      Stick,
      Blitzritter,
      Somnus,
      Sana,
      Ignis,
      HpUp,
    ]
    ctx.skill_builds = {}
    ctx.selected_skills = {}
    ctx.load_build(ctx.hero, [
      (Stick, (0, 0)),
      (Blitzritter, (1, 0))
    ])
    ctx.load_build(ctx.ally, [
      (Ignis, (0, 0)),
      (Somnus, (0, 1)),
      (Sana, (1, 0)),
    ])
    ctx.monster_kills = {}
    ctx.seeds = []
    ctx.debug = False
    if start_in_dungeon:
      ctx.goto_dungeon()
    else:
      ctx.goto_town()

  def reset(ctx):
    if type(ctx.child) is DungeonContext:
      ctx.goto_dungeon()
    elif type(ctx.child) is TownContext:
      ctx.goto_town()

  def goto_dungeon(ctx):
    ctx.child = DungeonContext(parent=ctx)

  def goto_town(ctx, returning=False):
    ctx.child = TownContext(parent=ctx, returning=returning)

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

  def draw(ctx, surface):
    super().draw(surface)
    if len(ctx.transits):
      transit = ctx.transits[0]
      transit.update()
      transit.draw(surface)
      if transit.done:
        ctx.transits.remove(transit)
