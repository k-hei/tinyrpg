import pygame
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import game.controls as controls
from config import WINDOW_SIZE, DEBUG, KNIGHT_BUILD, MAGE_BUILD, ROGUE_BUILD
from contexts import Context
from contexts.load import LoadContext
from contexts.pause import PauseContext
from contexts.inventory import InventoryContext
from contexts.custom import CustomContext
from dungeon.context import DungeonContext, DungeonData
from dungeon.stage import Stage
from dungeon.decor import Decor
from dungeon.features.room import Room
from dungeon.features.altarroom import AltarRoom
from dungeon.decoder import decode_floor
from town.context import TownContext
from cores.knight import Knight
from cores.mage import Mage
from cores.rogue import Rogue
from inventory import Inventory
from skills import get_skill_order
from game.data import GameData
from savedata.resolve import resolve_item, resolve_skill, resolve_elem
from transits.dissolve import DissolveOut

gamepad.config(preset=controls.TYPE_A)

class GameContext(Context):
  def __init__(ctx, data=None, feature=None, floor=None, seed=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = None
    ctx.savedata = None
    ctx.feature = feature
    ctx.floor = floor
    ctx.seed = seed
    if data is None:
      ctx.open(LoadContext(), on_close=lambda *data: ctx.load(*data))
    elif type(data) is GameData:
      ctx.store = data
      ctx.savedata = GameData.encode(data)
    else:
      ctx.store = GameData.decode(data)
      ctx.savedata = data

  def init(ctx):
    if ctx.savedata or ctx.feature or ctx.floor:
      ctx.load()

  def load(ctx, savedata=None):
    if savedata is None:
      savedata = ctx.savedata

    floor = None
    ctx.store = GameData.decode(savedata)
    ctx.update_skills()

    if ctx.feature:
      feature = ctx.feature
      ctx.feature = None
      app = ctx.get_head()
      return app.load(
        loader=feature().create_floor(),
        on_end=lambda floor: (
          ctx.goto_dungeon(floors=[floor], generator=feature),
          app.transition([DissolveOut()])
        )
      )

    if ctx.floor:
      Floor = ctx.floor
      ctx.floor = None
      app = ctx.get_head()
      return app.load(
        loader=Floor.generate(ctx.store, seed=ctx.seed),
        on_end=lambda floor: (
          ctx.goto_dungeon(floors=[floor], generator=Floor),
          app.transition([DissolveOut()])
        )
      )

    if type(savedata.dungeon) is dict:
      return ctx.goto_dungeon(
        floor_index=savedata.dungeon["floor_index"] if "floor_index" in savedata.dungeon else 0,
        floors=[decode_floor(f) for f in savedata.dungeon["floors"]],
        memory=[[tuple(c) for c in f] for f in (savedata.dungeon["memory"] if "memory" in savedata.dungeon else [])]
      )
    elif savedata.dungeon:
      return ctx.goto_dungeon(
        floor_index=savedata.dungeon.floor_index,
        floors=savedata.dungeon.floors,
        memory=savedata.dungeon.memory
      )

    if savedata.place == "dungeon":
      ctx.goto_dungeon(floors=floor and [floor])
    elif savedata.place == "town":
      ctx.goto_town()

  def save(ctx):
    ctx.savedata = ctx.store.encode()
    return ctx.savedata

  def reset(ctx):
    ctx.load()

  def goto_dungeon(ctx, floors=[], floor_index=0, memory=[], generator=None):
    if floors:
      floor = floors[floor_index]
      floor.generator = floor.generator or generator and generator.__name__
      dungeon = DungeonContext(
        store=ctx.store,
        floors=floors,
        floor_index=floor_index,
        memory=memory
      )
      ctx.store.place = dungeon
      ctx.open(dungeon)
    else:
      app = ctx.get_head()
      app.load(
        loader=AltarRoom().create_floor(),
        on_end=lambda floor: (
          ctx.goto_dungeon(floors=[floor]),
          not app.transits and app.transition([DissolveOut()])
        )
      )

  def goto_town(ctx, returning=False):
    town = TownContext(store=ctx.store, returning=returning)
    ctx.store.place = town
    ctx.open(town)

  def record_kill(ctx, target):
    target_type = type(target)
    if target_type in ctx.store.kills:
      ctx.store.kills[target_type] += 1
    else:
      ctx.store.kills[target_type] = 1

  def get_skill(ctx, actor):
    actor_id = type(actor).__name__
    return ctx.store.selected_skill[actor_id] if actor_id in ctx.store.selected_skill else None

  def set_skill(ctx, actor, skill):
    ctx.store.selected_skill[type(actor).__name__] = skill

  def learn_skill(ctx, skill):
    if not skill in ctx.store.skills:
      ctx.store.new_skills.append(skill)
      ctx.store.skills.append(skill)
      ctx.store.skills.sort(key=get_skill_order)

  def load_build(ctx, actor, build):
    ctx.store.builds[type(actor).__name__] = build
    actor.skills = [skill for skill, cell in build]
    active_skills = actor.get_active_skills()
    ctx.set_skill(actor, active_skills[0] if active_skills else None)

  def update_skills(ctx):
    for core in ctx.store.party:
      ctx.load_build(actor=core, build=ctx.store.builds[type(core).__name__])

  def handle_press(ctx, button):
    if super().handle_press(button) != None:
      return
    if (keyboard.get_pressed(button) + gamepad.get_state(button) > 1
    or type(ctx.child) not in (DungeonContext, TownContext)
    or type(ctx.child) is DungeonContext and ctx.child.get_depth() > 0
    or type(ctx.child) is TownContext and ctx.child.get_depth() > 1
    ):
      return
    if button in (pygame.K_ESCAPE, pygame.K_BACKSPACE) or gamepad.get_state(gamepad.controls.item):
      return ctx.handle_inventory()
    if button == pygame.K_b or gamepad.get_state(gamepad.controls.equip):
      return ctx.handle_custom()

  def handle_pause(ctx):
    child = ctx.get_tail()
    child.open(PauseContext())

  def handle_inventory(ctx):
    ctx.get_tail().open(InventoryContext(store=ctx.store))

  def handle_custom(ctx):
    ctx.get_tail().open(CustomContext(
      store=ctx.store,
      on_close=ctx.update_skills
    ))

  def update(ctx):
    super().update()
    if ctx.store:
      ctx.store.time += 1 / ctx.get_head().fps
