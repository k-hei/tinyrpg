from random import random
from lib.cell import manhattan
import lib.vector as vector
from helpers.findactor import find_actor
from contexts import Context
from comps.hud import Hud
from comps.minilog import Minilog
from comps.minimap import Minimap
from comps.skillbanner import SkillBanner
from anims.item import ItemAnim
from dungeon.actors import DungeonActor
from vfx.talkbubble import TalkBubble

class ExploreBase(Context):
  def __init__(ctx, store=None, stage=None, stage_view=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.store = store
    ctx.stage = stage
    ctx.stage_view = stage_view

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
  def camera(ctx):
    return ctx.stage_view.camera

  @property
  def anims(ctx):
    return ctx.stage_view.anims

  @property
  def vfx(ctx):
    return ctx.stage_view.vfx

  @property
  def comps(ctx):
    return ctx._comps if "_comps" in dir(ctx) else ctx.parent.comps

  @comps.setter
  def comps(ctx, comps):
    ctx._comps = comps

  @property
  def hud(ctx):
    return next((c for c in ctx.comps if type(c) is Hud), None)

  @property
  def minilog(ctx):
    return next((c for c in ctx.comps if type(c) is Minilog), None)

  @property
  def minimap(ctx):
    return next((c for c in ctx.comps if type(c) is Minimap), None)

  @property
  def skill_banner(ctx):
    return next((c for c in ctx.comps if type(c) is SkillBanner), None)

  @property
  def talkbubble(ctx):
    return next((v for v in ctx.vfx if type(v) is TalkBubble), None)

  @property
  def facing_elem(ctx):
    facing_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    facing_elems = ctx.stage.get_elems_at(facing_cell)
    return next((e for e in facing_elems if (
      e.active
      and (not isinstance(e, DungeonActor) or e.faction == "ally")
    )), None)

  @property
  def facing_actor(ctx):
    facing_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    facing_elems = ctx.stage.get_elems_at(facing_cell)
    return next((e for e in facing_elems if isinstance(e, DungeonActor)), None)

  def find_closest_enemy(ctx, actor):
    enemies = [e for e in ctx.stage.elems if (
      isinstance(e, DungeonActor)
      and not e.is_dead()
      and not e.allied(actor)
    )]

    if not enemies:
      return None

    if len(enemies) > 1:
      enemies.sort(key=lambda e: manhattan(e.cell, actor.cell) + random() / 2)

    return enemies[0]

  def find_enemies_in_range(ctx):
    room = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells), None)
    return [e for e in ctx.stage.elems if
      isinstance(e, DungeonActor)
      and e.faction == DungeonActor.FACTION_ENEMY
      and not e.dead
      and room and e.cell in room.cells
    ]

  def handle_obtain(ctx, item, target, on_end=None):
    obtained = ctx.store.obtain(item)
    if obtained:
      old_facing = ctx.hero.facing
      ctx.hero.facing = (0, 1)
      ctx.anims.append([
        ItemAnim(
          target=target,
          item=item(),
          duration=60,
          on_end=lambda: (
            setattr(ctx.hero, "facing", old_facing),
            on_end and on_end(),
          )
        )
      ])
      ctx.minilog.print(message=("Obtained ", item().token(), "."))
    return obtained

  def update_bubble(ctx):
    facing_elem = ctx.facing_elem
    pending_anims = [a for g in ctx.anims for a in g if not a.done]

    can_show_bubble = not pending_anims and not ctx.hero.item and not (ctx.child and ctx.child.child)
    if ctx.talkbubble and ctx.talkbubble.target is facing_elem and can_show_bubble:
      return

    if ctx.talkbubble:
      ctx.talkbubble.done = True

    if facing_elem and can_show_bubble:
      ctx.vfx.append(TalkBubble(
        target=facing_elem,
        cell=facing_elem.cell,
        flipped=ctx.camera.is_pos_beyond_yrange(pos=vector.scale(facing_elem.cell, ctx.stage.tile_size)),
      ))
