import lib.gamepad as gamepad
import lib.input as input
import lib.vector as vector
from lib.direction import invert as invert_direction

import game.controls as controls
from game.world import construct_world
from contexts import Context
from contexts.load import LoadContext
from contexts.pause import PauseContext
from contexts.inventory import InventoryContext
from contexts.custom import CustomContext
from contexts.dungeon.context import DungeonContext
from contexts.loading import LoadingContext
from contexts.controls import ControlsContext
from contexts.dialogue import DialogueContext
from contexts.cutscene import CutsceneContext
from contexts.explore.manifest import manifest_room
from contexts.explore.roomdata import load_rooms, rooms, RoomData
from resolve.floor import resolve_floor
from dungeon.decoder import decode_floor
from dungeon.gen.floorgraph import FloorGraph
from skills import get_skill_order
from skills.weapon import Weapon
from debug import bench
from game.data import GameData
from transits.dissolve import DissolveOut
import debug

from town.context import TownContext
from town.topview.stage import Stage as TownTopViewArea
from town.sideview.stage import Area as TownSideViewArea
from town.areas.outskirts import OutskirtsArea
from town.graph import WorldGraph


load_rooms()
gamepad.config(preset=controls.TYPE_A)

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

    ctx.graph = None

  def init(ctx):
    ctx.graph = construct_world()
    if ctx.savedata or ctx.feature or ctx.floor:
      ctx.load()

  def load(ctx, savedata=None):
    if savedata is None:
      savedata = ctx.savedata

    if savedata is None:
      debug.log("No save data to load!")
      return

    floor = None
    ctx.savedata = savedata
    ctx.store = GameData.decode(savedata)
    ctx.update_skills()
    ctx.store.controls and gamepad.config(preset=ctx.store.controls)

    if ctx.stage:
      stage = ctx.stage
      ctx.stage = None
      return ctx.goto_dungeon(floors=FloorGraph(nodes=[stage]))

    if ctx.feature:
      feature = ctx.feature
      ctx.feature = None
      app = ctx.get_head()
      return app.load(
        loader=feature().create_floor(),
        on_end=lambda floor: (
          ctx.goto_dungeon(floors=FloorGraph(nodes=[floor]), generator=feature),
          app.transition([DissolveOut()])
        )
      )

    if ctx.floor:
      Floor = ctx.floor
      ctx.floor = None
      app = ctx.get_head()
      bench("Generate floor")
      return ctx.open(LoadingContext(
        loader=Floor.generate(ctx.store, seed=ctx.seed),
        on_end=lambda floor: (
          bench("Generate floor"),
          debug.log(f"Using seed {ctx.seed}"),
          ctx.goto_dungeon(floors=FloorGraph(nodes=[floor]), generator=Floor),
        )
      ))

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
    else:
      ctx.goto_dungeon(floors=FloorGraph(
        nodes=[manifest_room(rooms["tutorial1"])]
      ))

  def save(ctx):
    if gamepad.controls is not controls.TYPE_A:
      ctx.store.controls = gamepad.controls
    ctx.savedata = ctx.store.encode()
    return ctx.savedata

  def reset(ctx):
    ctx.load()

  def goto_dungeon(ctx, floors=[], floor_index=0, memory=[], generator=None):
    if floors:
      floor = floors.nodes[floor_index]
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
      stage = manifest_room(rooms["shrine"])
      ctx.goto_dungeon(floors=FloorGraph(nodes=[stage]))

    app = ctx.get_head()
    not app.transits and app.transition([DissolveOut()])

  def goto_town(ctx, area=None, port=None, returning=False):
    if returning and area is None and port is None:
      area, port = OutskirtsArea, "tower"

    town = TownContext(store=ctx.store, area=area, port=port)
    ctx.store.place = town
    ctx.open(town)

  def load_area(ctx, area, port_id=None):
    debug.log("load area", (area.key, port_id) if port_id else area.key)

    port = area.ports[port_id] if port_id else None
    hero = ctx.store.hero
    if hero:
      hero.facing = invert_direction(port.direction) if port else (0, 1)

    if isinstance(area, RoomData):
      stage = manifest_room(area)
      if port:
        stage.entrance = vector.add(port.cell, hero.facing)
      dungeon = DungeonContext(
        store=ctx.store,
        stage=stage,
      )
      ctx.store.place = dungeon
      ctx.open(dungeon)

    if isinstance(area, type) and issubclass(area, (TownSideViewArea, TownTopViewArea)):
      ctx.goto_town(area, port_id)

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

  def forget_skill(ctx, skill):
    return ctx.store.forget_skill(skill)

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

    # TODO: only town and dungeon contexts should be able to access pause/inventory
    # what kinds of generic assumptions can we make about potential use cases
    blocking_contexts = (
      PauseContext,
      InventoryContext,
      LoadContext,
      ControlsContext,
      LoadingContext,
      CutsceneContext,
      DialogueContext,
    )
    if isinstance(ctx.get_tail(), blocking_contexts) or ctx.get_depth() > 2:
      return

    controls = input.resolve_controls(button)
    for control in controls:
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
