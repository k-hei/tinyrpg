import pygame
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import lib.input as input
import game.controls as controls
from contexts import Context
from contexts.load import LoadContext
from contexts.pause import PauseContext
from contexts.inventory import InventoryContext
from contexts.custom import CustomContext
from contexts.dungeon import DungeonContext
from dungeon.gen.manifest import manifest_stage_from_room
from dungeon.decoder import decode_floor
from contexts.explore.roomdata import load_rooms, rooms
from town.context import TownContext
from skills import get_skill_order
from skills.weapon import Weapon
from debug import bench
from game.data import GameData
from transits.dissolve import DissolveOut

load_rooms()
gamepad.config(preset=controls.TYPE_A)

input.config(
  buttons={
    input.BUTTON_UP: [pygame.K_UP, pygame.K_w],
    input.BUTTON_LEFT: [pygame.K_LEFT, pygame.K_a],
    input.BUTTON_DOWN: [pygame.K_DOWN, pygame.K_s],
    input.BUTTON_RIGHT: [pygame.K_RIGHT, pygame.K_d],
    input.BUTTON_A: [pygame.K_RETURN, pygame.K_SPACE],
    input.BUTTON_B: [pygame.K_RSHIFT, pygame.K_LSHIFT],
    input.BUTTON_X: [pygame.K_q],
    input.BUTTON_Y: [pygame.K_e],
    input.BUTTON_L: [pygame.K_TAB],
    input.BUTTON_R: [pygame.K_LCTRL, pygame.K_RCTRL],
    input.BUTTON_START: [pygame.K_ESCAPE, pygame.K_BACKSPACE],
    input.BUTTON_SELECT: [pygame.K_BACKQUOTE, pygame.K_BACKSLASH],
  },
  controls={
    input.CONTROL_CONFIRM: [input.BUTTON_A],
    input.CONTROL_CANCEL: [input.BUTTON_B],
    input.CONTROL_MANAGE: [input.BUTTON_Y],
    input.CONTROL_RUN: [input.BUTTON_B],
    input.CONTROL_TURN: [input.BUTTON_R],
    input.CONTROL_ITEM: [input.BUTTON_R, input.BUTTON_X],
    input.CONTROL_WAIT: [input.BUTTON_R, input.BUTTON_A],
    input.CONTROL_SHORTCUT: [input.BUTTON_R, input.BUTTON_Y],
    input.CONTROL_ALLY: [input.BUTTON_L],
    input.CONTROL_SKILL: [input.BUTTON_Y],
    input.CONTROL_INVENTORY: [input.BUTTON_X],
    input.CONTROL_PAUSE: [input.BUTTON_START],
    input.CONTROL_MINIMAP: [input.BUTTON_SELECT],
  }
)

class GameContext(Context):
  def __init__(ctx, data=None, feature=None, floor=None, stage=None, seed=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = None
    ctx.savedata = None
    ctx.feature = feature
    ctx.floor = floor
    ctx.stage = stage
    ctx.seed = seed
    if data is None:
      ctx.open(LoadContext(), on_close=lambda *data: data and ctx.load(*data))
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
    ctx.store.controls and gamepad.config(preset=ctx.store.controls)

    if ctx.stage:
      stage = ctx.stage
      ctx.stage = None
      return ctx.goto_dungeon(floors=[stage])

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
      bench("Generate floor")
      return app.load(
        loader=Floor.generate(ctx.store, seed=ctx.seed),
        on_end=lambda floor: (
          bench("Generate floor"),
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
    if gamepad.controls is not controls.TYPE_A:
      ctx.store.controls = gamepad.controls
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
        stage=floor,
        # floors=floors,
        # floor_index=floor_index,
        # memory=memory
      )
      ctx.store.place = dungeon
      ctx.open(dungeon)
    else:
      app = ctx.get_head()
      stage = manifest_stage_from_room(room=rooms["shrine"])
      ctx.goto_dungeon(floors=[stage]),
      not app.transits and app.transition([DissolveOut()])

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
    actor.skills = sorted([skill for skill, cell in build], key=get_skill_order)
    active_skills = actor.get_active_skills()
    ctx.set_skill(actor, skill=next((s for s in active_skills if not issubclass(s, Weapon)), None))

  def update_skills(ctx):
    for core in ctx.store.party:
      core_id = type(core).__name__
      ctx.load_build(actor=core, build=ctx.store.builds[core_id] if core_id in ctx.store.builds else [])

  def handle_press(ctx, button):
    if super().handle_press(button) != None:
      return False

    if input.get_state(button) > 1:
      return False

    control = input.resolve_control(button)

    if type(ctx.get_tail()) in (PauseContext, InventoryContext) or ctx.get_depth() > 2:
      return

    if control == input.CONTROL_PAUSE:
      return ctx.handle_pause()

    if control == input.CONTROL_INVENTORY:
      return ctx.handle_inventory()

  def handle_pause(ctx):
    if not isinstance(ctx.get_tail(), PauseContext):
      ctx.get_tail().open(PauseContext(store=ctx.store))

  def handle_inventory(ctx):
    if not isinstance(ctx.get_tail(), InventoryContext):
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
