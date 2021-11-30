from helpers.findactor import find_actor
import lib.vector as vector
from contexts import Context
from contexts.explore import ExploreContext
from contexts.explore.stageview import StageView
from contexts.combat import CombatContext
from contexts.dungeon.camera import Camera
from comps.hud import Hud
from comps.minilog import Minilog
from comps.minimap import Minimap
from dungeon.actors import DungeonActor
from dungeon.actors.knight import Knight
from dungeon.fov import shadowcast
from dungeon.room import Blob as Room
from vfx.talkbubble import TalkBubble
from config import WINDOW_SIZE, WINDOW_HEIGHT, VISION_RANGE

class DungeonContext(Context):
  def __init__(ctx, store, stage, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.camera = Camera(WINDOW_SIZE)
    ctx.memory = {}
    ctx.stage_view = StageView(stage=stage, camera=ctx.camera)
    ctx.hero_cell = None
    ctx.hero_facing = None
    ctx.comps = []

  @property
  def hero(ctx):
    return find_actor(
      char=ctx.store.party[0],
      stage=ctx.stage
    ) if ctx.store.party else None

  @property
  def visited_cells(ctx):
    stage_id = ctx.stage.__hash__()
    visited_cells = ctx.memory[stage_id] if stage_id in ctx.memory else None # next((cs for (s, cs) in ctx.memory if s is ctx.stage), None)
    if visited_cells is None:
      ctx.memory[stage_id] = (visited_cells := [])
    return visited_cells

  @property
  def anims(ctx):
    return ctx.stage_view.anims

  @property
  def vfx(ctx):
    return ctx.stage_view.vfx

  @property
  def minilog(ctx):
    return next((c for c in ctx.comps if type(c) is Minilog), None)

  @property
  def minimap(ctx):
    return next((c for c in ctx.comps if type(c) is Minimap), None)

  @property
  def hud(ctx):
    return next((c for c in ctx.comps if type(c) is Hud), None)

  @property
  def talkbubble(ctx):
    return next((v for v in ctx.vfx if type(v) is TalkBubble), None)

  def enter(ctx):
    hero = Knight(core=ctx.store.party[0])
    stage_entrance = next((cell for cell, tile in ctx.stage.tiles.enumerate() if tile.__name__ == "Exit"), None)
    stage_entrance and ctx.stage.spawn_elem_at(stage_entrance, hero)
    ctx.comps = [
      Hud(party=ctx.store.party, hp=True),
      Minilog(pos=(8, WINDOW_HEIGHT - 8 - Minilog.sprite.get_height() / 2)),
      Minimap(
        stage=ctx.stage,
        hero=ctx.hero,
        visited_cells=ctx.visited_cells
      )
    ]
    ctx.handle_explore()

  def refresh_fov(ctx):
    room = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells), None)
    if room:
      visible_cells = room.cells + room.visible_outline
      ctx.camera.focus(room)
    else:
      visible_cells = shadowcast(ctx.stage, ctx.hero.cell, VISION_RANGE)
      room = next((t for t in ctx.camera.target if isinstance(t, Room)), None)
      if room:
        ctx.camera.blur(room)
      ctx.camera.focus(ctx.hero)

    ctx.hero.visible_cells = visible_cells
    ctx.update_visited_cells(visible_cells)

  def handle_explore(ctx):
    ctx.open(ExploreContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      on_end=ctx.handle_combat,
    ))
    ctx.minimap.enter()

  def handle_combat(ctx):
    ctx.open(CombatContext(
      store=ctx.store,
      stage=ctx.stage,
      stage_view=ctx.stage_view,
      on_end=ctx.handle_explore,
    ))
    ctx.minimap.exit()
    ctx.hud.enter()

  def update_bubble(ctx):
    facing_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    facing_elems = ctx.stage.get_elems_at(facing_cell)
    facing_elem = next((e for e in facing_elems if (
      e.active
      and (not isinstance(e, DungeonActor) or e.faction == "ally")
    )), None)

    if ctx.talkbubble and ctx.talkbubble.target is facing_elem and not ctx.anims and not ctx.hero.item:
      return

    if ctx.talkbubble:
      ctx.talkbubble.done = True

    if facing_elem and not ctx.anims and not ctx.hero.item:
      ctx.vfx.append(TalkBubble(
        target=facing_elem,
        cell=facing_cell,
      ))

  def update_visited_cells(ctx, cells):
    ctx.visited_cells.extend([c for c in cells if c not in ctx.visited_cells])

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

    for comp in ctx.comps:
      comp.update()

    if ctx.hero_facing != ctx.hero.facing:
      ctx.hero_facing = ctx.hero.facing
      ctx.update_bubble()

    if ctx.hero.cell != ctx.hero_cell:
      ctx.hero_cell = ctx.hero.cell
      ctx.update_bubble()
      ctx.refresh_fov()

    ctx.camera.update()
    ctx.stage_view.update()
    super().update()

  def view(ctx):
    return ctx.stage_view.view(
      hero=ctx.hero,
      visited_cells=ctx.visited_cells,
    ) + [c.view() for c in ctx.comps] + super().view()
