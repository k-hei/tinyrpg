import pygame
import lib.vector as vector
import lib.input as input
from lib.direction import invert as invert_direction
from lib.cell import neighborhood, manhattan, is_adjacent, upscale, downscale
from helpers.combat import find_damage, will_miss, will_crit, will_block, animate_snap
from helpers.stage import is_tile_walkable_to_actor, is_cell_walkable_to_actor
from resolve.skill import resolve_skill
import debug

import assets

from contexts.combat.grid import CombatGridCellAnim, CombatGridCellEnterAnim, CombatGridCellExitAnim
from contexts.explore.base import (
  ExploreBase,
  COMMAND_MOVE, COMMAND_MOVE_TO, COMMAND_ATTACK, COMMAND_SKILL, COMMAND_WAIT
)
from contexts.skill import SkillContext
from contexts.gameover import GameOverContext
from contexts.ally import AllyContext
from contexts.pause import PauseContext
from contexts.cutscene import CutsceneContext
from comps.damage import DamageValue
from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage
from dungeon.props.door import Door
from dungeon.props.soul import Soul
from dungeon.props.itemdrop import ItemDrop
from skills.weapon import Weapon
from locations.default.tile import Tile
import locations.default.tileset as tileset
from anims.move import MoveAnim
from anims.step import StepAnim
from anims.path import PathAnim
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim
from anims.shake import ShakeAnim
from anims.flicker import FlickerAnim
from vfx.flash import FlashVfx
from colors.palette import RED, GREEN, BLUE, GOLD, PURPLE, CYAN
from config import (
  FLINCH_PAUSE_DURATION, FLICKER_DURATION, NUDGE_DURATION, SIDESTEP_DURATION, SIDESTEP_AMPLITUDE,
  CRIT_MODIFIER,
  TILE_SIZE,
  WINDOW_WIDTH, WINDOW_HEIGHT,
)

from math import inf
from lib.sprite import Sprite
from easing.expo import ease_out


def find_damage_text(damage):
  if damage == 0:
    return "BLOCK"
  elif damage == None:
    return "MISS"
  else:
    return int(damage)

class CombatContext(ExploreBase):
  def __init__(ctx, path=False, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.should_path = path
    ctx.exiting = False
    ctx.turns = 0
    ctx.turns_completed = 0
    ctx.command_queue = []
    ctx.command_pending = None
    ctx.command_gen = None
    ctx.buttons_rejected = {}

  def enter(ctx):
    if not ctx.hero:
      return

    walk_speed = 3 if ctx.ally else 2
    actor_cells = {}

    create_brandish = lambda actor: (
      actor.core.BrandishAnim(
        target=actor,
        on_start=(lambda: (
          ctx.anims[0].append(JumpAnim(
            target=actor,
            height=28,
            delay=actor.core.BrandishAnim.frames_duration[0],
            duration=actor.core.BrandishAnim.jump_duration,
          ))
        )) if type(actor) is Mage else None,
        on_end=lambda: (
          actor.stop_move(),
          actor.core.anims.append(actor.core.IdleDownAnim()),
        )
      )
    )

    hero_brandish = ctx.hero.weapon and create_brandish(ctx.hero)
    ally_brandish = ctx.ally and ctx.ally.weapon and create_brandish(ctx.ally)

    if ctx.should_path:
      hero_cell = animate_snap(ctx.hero, anims=ctx.anims, speed=walk_speed)
      if hero_cell:
        actor_cells[ctx.hero] = hero_cell
      # actor_cells[ctx.hero] = vector.round(ctx.hero.cell)

      if ctx.ally:
        ally_cell = animate_snap(ctx.ally, anims=ctx.anims, speed=walk_speed)
        if ally_cell:
          actor_cells[ctx.ally] = ally_cell

    if ctx.ally and ctx.should_path:
      start_cells = [c for c in neighborhood(ctx.hero.cell, diagonals=True) + [ctx.hero.cell] if
        not next((e for e in ctx.stage.get_elems_at(c) if
          isinstance(e, Door)
          or e.solid and e is not ctx.hero
        ), None)
        and not ctx.stage.is_tile_at_solid(c)
      ]

      hero_path = ctx.stage.pathfind(
        start=actor_cells[ctx.hero],
        goal=start_cells.pop(0),
        whitelist=ctx.stage.find_walkable_room_cells(room=ctx.room, ignore_actors=True)
      )

      ally_path = ctx.stage.pathfind(
        start=actor_cells[ctx.ally],
        goal=start_cells.pop(0),
        whitelist=ctx.stage.find_walkable_room_cells(room=ctx.room, ignore_actors=True) + [ctx.ally.cell]
      )

      ctx.anims.append([
        *([PathAnim(
          target=ctx.hero,
          path=hero_path,
          period=TILE_SIZE // walk_speed,
          on_end=lambda: hero_brandish and ctx.anims[0].append(hero_brandish)
        )] if hero_path else []),
        *([PathAnim(
          target=ctx.ally,
          path=ally_path,
          period=TILE_SIZE // walk_speed,
          on_end=lambda: ally_brandish and ctx.anims[0].append(ally_brandish)
        )] if ally_path else []),
      ])

    elif hero_brandish or ally_brandish:
      ctx.anims.append([
        *([hero_brandish] if hero_brandish else []),
        *([ally_brandish] if ally_brandish else []),
      ])

    else:
      ctx.hero.stop_move()

    ctx.enter_grid()

  def exit(ctx, ally_rejoin=False):
    if ctx.exiting:
      return

    for elem in ctx.stage.elems:
      if elem.expires:
        elem.dissolve()

    for actor in ctx.party:
      actor.dispel_ailment()

    hero_adjacents = [n for n in neighborhood(ctx.hero.cell) if ctx.stage.is_cell_empty(n)]
    if ally_rejoin and ctx.ally and hero_adjacents:
      target_cell = sorted(hero_adjacents, key=lambda c: manhattan(c, ctx.ally.cell))[0]
      ally_path = ctx.stage.pathfind(
        start=ctx.ally.cell,
        goal=target_cell,
        predicate=lambda cell: is_cell_walkable_to_actor(ctx.stage, cell, ctx.ally)
      ) or ctx.stage.pathfind(
        start=ctx.ally.cell,
        goal=target_cell,
        predicate=lambda cell: is_tile_walkable_to_actor(ctx.stage, cell, ctx.ally)
      )
      ally_path and ctx.anims.append([PathAnim(
        target=ctx.ally,
        period=TILE_SIZE / 3,
        path=ally_path
      )])

    room_enemies = [e for e in ctx.stage.elems
      if isinstance(e, DungeonActor)
      and e.faction == "enemy"
      and e.cell in ctx.room.cells]

    ctx.anims.append([(lambda e: PathAnim(
      target=e,
      period=TILE_SIZE / 3,
      path=ctx.stage.pathfind(
        start=e.cell,
        goal=e.ai_spawn,
        whitelist=ctx.stage.find_walkable_room_cells(room=ctx.room, ignore_actors=True)
      ),
      on_end=lambda: (
        setattr(e, "aggro", 0),
        ctx.anims[-1].append(PauseAnim(
          duration=2,  # HACK: prevent path anim from setting facing post on_end
          on_end=lambda: setattr(e, "facing", (0, 1))
        )),
      ),
    ))(e) for e in room_enemies if e.ai_spawn and e.cell != e.ai_spawn])

    ctx.exiting = True

    ctx.comps.skill_badge.exit()
    ctx.comps.sp_meter.exit()
    ctx.comps.hud.exit(on_end=lambda: (
      ctx.hero.core.anims.clear(),
      ctx.ally and ctx.ally.core.anims.clear(),
    ))
    ctx.exit_grid(on_end=ctx.close)

  def enter_grid(ctx, on_end=None):
    ctx.animate_grid(enter=True, on_end=on_end)

  def exit_grid(ctx, on_end=None):
    ctx.animate_grid(enter=False, on_end=on_end)

  def animate_grid(ctx, enter=True, on_end=None):
    if not ctx.room or not ctx.hero:
      return

    anim_group = ctx.anims[-1 if enter else 0] if ctx.anims else []
    not anim_group in ctx.anims and ctx.anims.append(anim_group)

    room = ctx.room
    room_cells = room.cells
    if not ctx.stage.is_overworld:
      room_cells = [c for c in room_cells
        if ctx.stage.is_cell_walkable(c, scale=TILE_SIZE)]

    room_cells = sorted(room_cells, key=lambda c: c[1] * ctx.stage.width + c[0])
    room_cells_by_dist = {}
    origin_cell = sorted([room_cells[0], room_cells[-1]],
      key=lambda c: manhattan(c, ctx.hero.cell))[0]

    for cell in room_cells:
      dist = manhattan(origin_cell, cell)
      if dist in room_cells_by_dist:
        room_cells_by_dist[dist].append(cell)
      else:
        room_cells_by_dist[dist] = [cell]

    CombatGridCellAnim = (CombatGridCellEnterAnim
      if enter
      else CombatGridCellExitAnim)

    for dist in sorted(room_cells_by_dist.keys()):
      cells = room_cells_by_dist[dist]
      anim_group += [CombatGridCellAnim(
        target=cell,
        delay=dist * 4
      ) for cell in cells]

    anim_group[-1].on_end = on_end

  def open(ctx, child, on_close=None):
    if type(child) is PauseContext:
      return False
    ctx.comps.skill_badge.exit()
    return super().open(child, on_close=lambda *data: (
      (type(child) is not SkillContext or data == (None,)) and not ctx.exiting and ctx.reload_skill_badge(),
      on_close and on_close(*data), # TODO: clean up skill context output signature
    ))

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.anims or ctx.exiting:
      return

    tapping = input.get_state(button) == 1
    controls = input.resolve_controls(button)
    ctrl = (input.get_state(pygame.K_LCTRL)
      or input.get_state(pygame.K_RCTRL))

    if button == pygame.K_q and ctrl and tapping:
      return print(ctx.command_queue)

    delta = input.resolve_delta(button, fixed_axis=True) if button else (0, 0)
    if delta != (0, 0):
      if input.is_control_pressed(input.CONTROL_TURN):
        return ctx.handle_turn(delta)

      moved = ctx.handle_move(delta)
      if not moved and button not in ctx.buttons_rejected:
        ctx.buttons_rejected[button] = 0
      elif not moved and ctx.buttons_rejected[button] >= 30:
        return ctx.handle_push(fixed=True)

      return moved

    if input.CONTROL_WAIT in controls and tapping:
      return ctx.handle_wait()

    if input.CONTROL_SHORTCUT in controls and tapping:
      return ctx.handle_shortcut()

    if input.CONTROL_CONFIRM in controls:
      if not ctx.hero.item and tapping:
        acted = ctx.handle_action()
        if acted == False:
          ctx.buttons_rejected[button] = 0
        return acted
      elif input.get_state(button) >= 30 and not button in ctx.buttons_rejected:
        return ctx.handle_throw()

    if input.CONTROL_ITEM in controls:
      if ctx.hero.item:
        return ctx.handle_throw()
      else:
        return ctx.handle_pickup()

    if input.CONTROL_MANAGE in controls and tapping:
      return ctx.handle_skill()

    if input.CONTROL_ALLY in controls and input.get_state(button) > 15:
      return ctx.handle_charmenu()

  def handle_release(ctx, button):
    buttons_rejected = ctx.buttons_rejected.copy()
    if button in ctx.buttons_rejected:
      del ctx.buttons_rejected[button]

    if ctx.child:
      return ctx.child.handle_release(button)

    control = input.resolve_control(button)
    if control == input.CONTROL_ALLY and input.get_state(button) <= 15:
      return ctx.handle_charswap()

    if control == input.CONTROL_CONFIRM and input.get_state(button) < 15 and not button in buttons_rejected and ctx.hero.item:
      return ctx.handle_place()

  def handle_move(ctx, delta):
    hero = ctx.hero
    if hero is None:
      return False

    if hero.ailment == "freeze":
      return ctx.handle_struggle(actor=hero)

    target_cell = vector.add(hero.cell, delta)

    def on_move():
      ctx.update_bubble()
      ctx.make_noise(hero.cell, 0.5)
      if not ctx.find_enemies_in_range():
        ctx.exit()

    hero.facing = delta
    moved = ctx.move_cell(hero, delta, on_end=on_move)
    if not moved and ctx.stage.is_tile_at_pit(target_cell):
      moved = ctx.leap(actor=hero, on_end=on_move)

    moved and ctx.find_enemies_in_range() and ctx.step()
    return moved

  def move_to(ctx, actor, dest, run=False, on_end=None):
    if actor.cell == dest or actor.ai_path and actor.cell == actor.ai_path[-1]:
      actor.ai_path = None
      if actor.cell == actor.ai_target:
        actor.ai_mode = DungeonActor.AI_LOOK
        actor.aggro = 0
      elif actor.cell == dest:
        on_end and on_end()
        return False

    pathfind = lambda: ctx.stage.pathfind(
      start=actor.cell,
      goal=dest,
      predicate=lambda cell: is_cell_walkable_to_actor(ctx.stage, cell, actor, ignore_actors=True)
    )

    if not actor.ai_path:
      actor.ai_path = pathfind()

    delta = ctx.find_move_to_delta(actor, dest)
    if actor.ai_path:
      cell_index = actor.ai_path.index(actor.cell) if actor.cell in actor.ai_path else -1
      next_cell = actor.ai_path[cell_index + 1] if (
        cell_index != -1
        and cell_index + 1 < len(actor.ai_path)
      ) else None
      delta = vector.subtract(next_cell, actor.cell) if next_cell else delta

    moved = False
    if delta != (0, 0):
      moved = ctx.move_cell(actor, delta, run, fixed=True, on_end=on_end)

    if not moved:
      actor.ai_path = pathfind()
      if not actor.ai_path:
        actor.ai_path = None
        actor.ai_target = None
        actor.ai_mode = DungeonActor.AI_LOOK
      on_end and on_end()

    return moved

  def find_move_to_delta(ctx, actor, dest):
    if actor.cell == dest:
      return (0, 0)

    delta_x, delta_y = (0, 0)
    actor_x, actor_y = actor.cell
    target_x, target_y = dest

    is_cell_walkable = lambda cell: (
      (not Tile.is_solid(ctx.stage.get_tile_at(cell)) or issubclass(ctx.stage.get_tile_at(cell), tileset.Pit)
        and not next((e for e in ctx.stage.get_elems_at(cell) if e.solid), None)
      ) if actor.floating else ctx.stage.is_cell_empty(cell)
    )

    def select_x():
      if target_x < actor_x and is_cell_walkable((actor_x - 1, actor_y)):
        return -1
      elif target_x > actor_x and is_cell_walkable((actor_x + 1, actor_y)):
        return 1
      else:
        return 0

    def select_y():
      if target_y < actor_y and is_cell_walkable((actor_x, actor_y - 1)):
        return -1
      elif target_y > actor_y and is_cell_walkable((actor_x, actor_y + 1)):
        return 1
      else:
        return 0

    delta_x = select_x()
    if not delta_x:
      delta_y = select_y()

    return (delta_x, delta_y)

  def leap(ctx, actor, on_end=None):
    middle_cell = vector.add(actor.cell, actor.facing)
    if next((True for e in ctx.stage.get_elems_at(middle_cell) if e.solid), False):
      return False

    delta = vector.scale(actor.facing, 2)
    moved = ctx.move_cell(actor, delta, jump=True, on_end=on_end)
    return moved

  def handle_turn(ctx, direction):
    ctx.hero.facing = direction
    ctx.update_bubble()
    return True

  def handle_struggle(ctx, actor):
    if actor.ailment not in ("freeze", "sleep"):
      return False
    actor.step_status(ctx)
    ctx.anims.append([
      ShakeAnim(duration=15, target=actor)
    ])
    if actor.ailment:
      ctx.step()
      return True
    else:
      return False

  def handle_action(ctx):
    hero = ctx.hero
    if hero is None:
      return False

    if hero.ailment == "freeze":
      return ctx.handle_struggle(actor=hero)

    origin_cell = downscale(hero.pos, scale=TILE_SIZE, floor=True)
    facing_cell = vector.add(origin_cell, ctx.hero.facing)

    facing_actor = ctx.facing_actor
    itemdrop = next((e for e in ctx.stage.get_elems_at(facing_cell) if isinstance(e, ItemDrop)), None)

    if ctx.hero.item:
      return ctx.handle_place()
    elif isinstance(facing_actor, DungeonActor):
      if facing_actor.faction == "enemy":
        return ctx.handle_attack()
    elif itemdrop:
      return ctx.handle_pickup()

    facing_elem = ctx.facing_elem
    action_result = facing_elem.effect(ctx, ctx.hero) if facing_elem else False
    if action_result != None:
      not ctx.anims and ctx.anims.append([])
      ctx.anims[0].insert(0, AttackAnim(
        target=ctx.hero,
        src=origin_cell,
        dest=facing_cell,
      ))
      ctx.update_bubble()

    return action_result

  def handle_attack(ctx):
    target_actor = ctx.facing_actor
    if not target_actor:
      return False

    attacked = ctx.attack(actor=ctx.hero, target=target_actor, on_end=ctx.step)
    if attacked:
      ctx.store.sp -= 1

    return attacked

  def attack(ctx, actor, target=None, atk_mod=1, crit_mod=1, animate=True, on_end=None):
    if actor.dead or actor.weapon is None:
      on_end and on_end()
      return False

    miss, crit, block = False, False, False
    if target:
      actor.face(target.cell)
      miss = will_miss(actor, target)
      block = will_block(actor, target) and not miss
      crit = will_crit(actor, target, mod=crit_mod) and not block
      if miss:
        damage = None
      elif block:
        damage = max(0, find_damage(actor, target, atk_mod) - target.find_shield().en)
      elif crit:
        damage = find_damage(actor, target, atk_mod=atk_mod * CRIT_MODIFIER)
      else:
        damage = find_damage(actor, target, atk_mod)

    attack_command = (actor, (COMMAND_ATTACK, target))
    ctx.command_queue.append(attack_command)

    connect = lambda: (
      target.alert(cell=actor.cell),
      ctx.make_noise(actor.cell, noise_factor=1.5),
      ctx.flinch(
        target=target,
        damage=damage,
        crit=crit,
        block=block,
        direction=actor.facing,
        on_end=lambda: (
          attack_command in ctx.command_queue and ctx.command_queue.remove(attack_command),
          on_end and on_end(),
        ),
      )
    )

    if animate:
      attack_delay = (
        actor.core.AttackAnim.frames_duration[0]
          if "AttackAnim" in dir(actor.core) and actor.facing == (0, 1)
          else 0
      )
      block_delay = (
        target.core.BlockAnim.frames_duration[0] + target.core.BlockAnim.frames_duration[1]
          if block and "BlockAnim" in dir(target.core)
          else 0
      )
      init_delay = max(attack_delay, block_delay)

      ctx.anims.extend([
        [*([PauseAnim(
          duration=init_delay,
          on_start=lambda: (
            actor.attack(),
            target.block(),
          )
        )] if init_delay else [])],
        [AttackAnim(
          target=actor,
          src=actor.cell,
          dest=vector.add(actor.cell, actor.facing),
          on_connect=(connect if target else None)
        )]
      ])
    else:
      block and target.block()
      connect()

    return True

  def flinch(ctx, target, damage, direction=None, crit=False, block=False, animate=True, on_end=None):
    show_text = lambda: ctx.vfx.append(DamageValue(
      text=find_damage_text(damage),
      pos=target.pos,
    ))

    if damage and crit:
      ctx.vfx.extend([
        DamageValue(
          text="CRITICAL!",
          pos=target.pos,
          offset=(4, -4),
          color=GOLD,
          delay=15
        ),
        FlashVfx()
      ])
      ctx.stage_view.shake(vertical=direction and bool(direction[1]))
      direction and ctx.nudge(target, direction)

    inflict = lambda: (
      direction and not target.ailment == DungeonActor.AILMENT_FREEZE and setattr(target, "facing", invert_direction(direction)),
      damage and target.damage(damage),
      show_text(),
    )

    cleanup = lambda: (
      ctx.kill(target, on_end=on_end)
        if (
          (target.is_dead() or ctx.stage.is_tile_at_pit(target.cell))
          and (not ctx.room or ctx.room.on_defeat(ctx, target))
          ) else on_end and on_end(),
    )

    if damage and target.item:
      ctx.place_item(actor=target)

    if animate:
      anim_group = next((g for g in ctx.anims if not next((a for a in g if a.target is target), None)), [])
      anim_group not in ctx.anims and ctx.anims.append(anim_group)
      anim_group.extend([
        *([ShakeAnim(
          target=target,
          magnitude=0.5,
          duration=15,
          on_start=inflict
        )] if block else [FlinchAnim(
          target=target,
          direction=direction,
          on_start=inflict
        )] if damage is not None else [AttackAnim(
          target=target,
          src=target.cell,
          dest=vector.add(target.cell, vector.tangent(direction)),
          duration=SIDESTEP_DURATION,
          amplitude=SIDESTEP_AMPLITUDE,
          on_start=inflict
        )] if direction else []),
        PauseAnim(
          duration=FLINCH_PAUSE_DURATION,
          on_end=cleanup
        )
      ])
    else:
      inflict()
      cleanup()

  def nudge(ctx, actor, direction, on_end=None):
    source_cell = downscale(actor.pos, scale=TILE_SIZE, floor=True)
    target_cell = vector.add(source_cell, direction)
    enemy_territory = (next((r for r in ctx.stage.rooms if actor.cell in r.cells), None)
      if actor.faction == "enemy"
      else None)

    if enemy_territory and target_cell not in enemy_territory.cells:
      return False

    if (not ctx.stage.is_cell_empty(target_cell, scale=TILE_SIZE)
    and not ctx.stage.is_tile_at_pit(target_cell)):
      return False

    actor.cell = vector.add(actor.cell, direction)

    not ctx.anims and ctx.anims.append([])
    ctx.anims[0].append(StepAnim(
      duration=NUDGE_DURATION,
      target=actor,
      src=source_cell,
      dest=target_cell,
      on_end=on_end
    ))
    return True

  def kill(ctx, target, on_end=None):
    if not ctx.hero:
      return

    target.kill(ctx)
    will_exit = not ctx.hero.allied(target) and not ctx.find_enemies_in_range()

    def remove_elem():
      target_skill = type(target).skill
      if target_skill and target.rare:
        skill = target_skill
        if skill not in ctx.store.skills:
          ctx.stage.spawn_elem_at(target.cell, Soul(contents=skill))
      if target is ctx.hero:
        if ctx.ally:
          ctx.handle_charswap()
        else:
          ctx.handle_gameover()
      ctx.stage.remove_elem(target)
      will_exit and not isinstance(ctx.get_tail(), CutsceneContext) and ctx.exit(ally_rejoin=True)
      on_end and on_end()

    not ctx.anims and ctx.anims.append([])
    ctx.anims[0].append(FlickerAnim(
      target=target,
      duration=FLICKER_DURATION,
      on_end=remove_elem
    ))

  def handle_charswap(ctx):
    if not ctx.hero:
      return False

    if (not ctx.ally
    or ctx.ally.dead
    or ctx.room and ctx.ally.cell not in ctx.room.cells):
      ctx.comps.hud.shake()
      return False

    if ctx.comps.hud.anims:
      return False

    ctx.store.switch_chars()
    ctx.parent.refresh_fov(reset_cache=True)
    ctx.reload_skill_badge()
    ctx.camera.blur()
    ctx.camera.focus(target=[ctx.room, ctx.hero], force=True)
    return True

  def handle_charmenu(ctx):
    if not ctx.ally:
      return False
    ctx.open(AllyContext())

  def handle_gameover(ctx):
    if type(ctx.child) is GameOverContext:
      return
    ctx.comps.skill_badge.exit()
    ctx.comps.hud.exit()
    ctx.comps.sp_meter.exit()
    ctx.open(GameOverContext())

  def handle_skill(ctx):
    hero = ctx.hero
    if hero is None:
      return

    if hero.ailment == "freeze":
      return ctx.handle_struggle(actor=hero)

    if hero.item:
      return False

    ctx.open(SkillContext(
      actor=hero,
      skills=hero.get_active_skills(),
      selected_skill=ctx.store.get_selected_skill(hero.core),
      on_close=lambda skill, dest: (
        skill and (
          not issubclass(skill, Weapon) and ctx.store.set_selected_skill(hero.core, skill),
          ctx.use_skill(hero, skill, dest, on_end=ctx.step),
        )
      )
    ))

  def use_skill(ctx, actor, skill, dest=None, on_end=None):
    skill = resolve_skill(skill) if isinstance(skill, str) else skill

    if actor.dead:
      return on_end and on_end()

    if actor.faction == "player":
      ctx.store.sp -= skill.cost

    skill_command = (actor, (COMMAND_SKILL, skill, dest))
    ctx.command_queue.append(skill_command)

    target_focus = None
    def on_start(*target):
      target = target[0] if target else None
      if target:
        nonlocal target_focus
        target_focus = upscale(target, TILE_SIZE)
        ctx.camera.focus(target=target_focus, force=True)

      ctx.display_skill(skill, user=actor)
      actor.faction == "player" and ctx.reload_skill_badge(delay=120)

    skill.effect(
      ctx,
      actor,
      dest,
      on_start=on_start,
      on_end=lambda: (
        skill_command in ctx.command_queue and ctx.command_queue.remove(skill_command),
        target_focus and ctx.camera.blur(target_focus),
        on_end and on_end(),
      )
    )

  def display_skill(ctx, skill, user):
    if not skill.name:
      return
    resolve_color = lambda faction: (
      BLUE if faction == "player"
      else RED if faction == "enemy"
      else GREEN if faction == "ally"
      else None
    )
    ctx.comps.skill_banner.enter(
      text=skill.name,
      color=resolve_color(user.faction),
    )

  def handle_shortcut(ctx):
    hero = ctx.hero
    if not hero:
      return False

    if hero.item:
      return False

    skill = ctx.store.get_selected_skill(hero.core)
    if not skill:
      return False

    if skill.range_min > 1:
      ctx.handle_skill()
    else:
      ctx.use_skill(hero, skill, on_end=ctx.step)

  def handle_wait(ctx):
    ctx.step()
    return True

  def handle_hallway(ctx):
    not ctx.find_enemies_in_range() and ctx.exit()

  def inflict_ailment(ctx, actor, ailment, color, on_end=None):
    if actor.is_dead() or actor.ailment == ailment:
      return False

    def inflict():
      if actor.ailment == ailment:
        for anim in anims:
          anim.end()
        return
      actor.inflict_ailment(ailment),
      ctx.vfx.append(DamageValue(
        text=ailment.upper(),
        color=color,
        pos=actor.pos,
        offset=(4, -4),
        delay=15,
      ))

    anims = [
      FlinchAnim(
        target=actor,
        duration=30,
        on_start=inflict
      ),
      PauseAnim(
        target=actor,
        duration=45,
        on_end=on_end,
      )
    ]

    if ailment == DungeonActor.AILMENT_FREEZE:
      ctx.anims[0].extend(anims)
    elif ailment == DungeonActor.AILMENT_POISON:
      ctx.anims.append(anims)

    return True

  def inflict_poison(ctx, actor, on_end=None):
    return ctx.inflict_ailment(actor, "poison", color=PURPLE, on_end=on_end)

  def inflict_freeze(ctx, actor, on_end=None):
    ctx.inflict_ailment(actor, "freeze", color=CYAN, on_end=on_end)
    actor.reset_charge()

  def update(ctx):
    super().update()
    ctx.update_command()

  def update_command(ctx):
    if not ctx.command_gen and not ctx.command_queue and ctx.turns_completed < ctx.turns:
      ctx.end_step()

    if not ctx.command_queue:
      ctx.command_discarded = False

    if ctx.command_queue and ctx.command_discarded:
      return

    if not ctx.command_pending and ctx.command_gen:
      try:
        ctx.command_pending = next(ctx.command_gen)
        if not ctx.command_pending:
          ctx.command_discarded = True
      except StopIteration:
        ctx.command_gen = None

    if ctx.command_pending:
      actor, command = ctx.command_pending
      queue_has_action = next((True for a, c in ctx.command_queue
        if c[0] not in (COMMAND_MOVE, COMMAND_WAIT)
      ), False)

      if not queue_has_action:
        chain = actor.turns > 1
        ctx.command_pending = None
        ctx.step_command(actor, command, chain)

  def step(ctx):
    ctx.turns += 1
    actors = [e for e in ctx.stage.elems if
      isinstance(e, DungeonActor)
      and e is not ctx.hero
      and e is not ctx.ally
      and not e.is_dead()
      and (not ctx.room or e.cell in ctx.room.cells)
      and e.cell in ctx.hero.visible_cells
    ]
    ctx.step_distribute(actors)
    ctx.step_execute(actors)

  def step_distribute(ctx, actors):
    for actor in actors:
      if actor.charge_skill or actor.faction == "ally" and not actor.aggro:
        actor.turns = 1
      else:
        spd = actor.stats.ag / ctx.hero.stats.ag
        actor.turns += spd

  def step_execute(ctx, actors):
    ctx.command_gen = ctx.step_generate(actors)

  def step_generate(ctx, actors):
    if ctx.ally and not ctx.ally.command:
      command = ctx.ally.step_charge()

      while not command:
        if ctx.command_queue and next((c for a, c in ctx.command_queue if a is ctx.ally), None):
          yield None
          continue

        command = ctx.step_ally(ctx.ally)

        if not command:
          break

        if command[0] in (COMMAND_ATTACK, COMMAND_SKILL) and ctx.command_queue:
          command = None
          yield None

      if command:
        yield ctx.ally, command

    for actor in actors:
      if actor.dead:
        continue

      while actor.turns >= 1:
        actor.turns -= 1

        if actor.dead:
          break

        actor.step_aggro()
        command = actor.step_charge()

        while not command:
          if actor.dead:
            break

          command = ctx.step_enemy(actor, force=True)
          if not command:
            break

        if command:
          yield actor, command

  def step_ally(ctx, actor):
    if not ctx.hero or not actor.can_step():
      return None

    enemies = [e for e in ctx.stage.elems
      if isinstance(e, DungeonActor)
      and not e.allied(ctx.hero)
      and e.cell in ctx.hero.visible_cells
      and e.hp
    ]
    adjacent_enemies = [e for e in enemies if is_adjacent(e.cell, ctx.ally.cell)]
    if adjacent_enemies:
      enemy = sorted(adjacent_enemies, key=lambda e: e.hp)[0]
      return (COMMAND_ATTACK, enemy)
    elif enemies and actor.behavior == "chase":
      enemy = sorted(enemies, key=lambda e: manhattan(e.cell, ctx.ally.cell) + e.hp / 10)[0]
      return (COMMAND_MOVE_TO, enemy.cell)

  def step_enemy(ctx, actor, force=False):
    if not actor.can_step() and not force:
      return None
    return actor.step(ctx)

  def step_command(ctx, actor, command, chain=False, on_end=None):
    on_end = on_end or (lambda: None)

    command_name, *command_args = command
    if actor.is_immobile() or actor.dead:
      return on_end()

    if command_name == COMMAND_MOVE:
      if chain:
        return ctx.move_cell(actor, *command_args, on_end=on_end)
      else:
        ctx.move_cell(actor, *command_args)
        return on_end()

    if command_name == COMMAND_MOVE_TO:
      if chain:
        return ctx.move_to(actor, *command_args, on_end=on_end)
      else:
        ctx.move_to(actor, *command_args)
        return on_end()

    if command_name == COMMAND_ATTACK:
      target = command_args and command_args[0]
      if target:
        return ctx.attack(actor, *command_args, on_end=on_end)
      else:
        return on_end()

    if command_name == COMMAND_SKILL:
      return ctx.use_skill(actor, *command_args, on_end=on_end)

    if command_name == COMMAND_WAIT:
      return on_end()

  def end_turn(ctx, actor):
    if ctx.exiting:
      return

    actor.step_status(ctx)
    effect_elem = next((e for e in ctx.stage.get_elems_at(actor.cell) if e.active and not e.solid), None)
    effect_elem and effect_elem.effect(ctx, actor)

  def end_step(ctx):
    ctx.turns_completed += 1

    actors = [e for e in ctx.stage.elems if isinstance(e, DungeonActor)]
    for actor in actors:
      actor.command = None
      ctx.end_turn(actor)

    non_actors = [e for e in ctx.stage.elems if e not in actors]
    for elem in non_actors:
      elem.step(ctx)

    ctx.stage.elems = [e for e in ctx.stage.elems if not e.done]

    hero = ctx.hero
    if not hero:
      return

    if hero.ailment == "sleep":
      ally = ctx.ally
      if ally and ally.can_step():
        ctx.handle_charswap()
      else:
        ctx.step()

  def view(ctx):
    return (ctx.view_grid() if ctx.hero else []) + super().view()

  def view_grid(ctx):
    if ctx.stage_view.darkened:
      return []

    room = ctx.room
    if not room or ctx.stage.is_overworld and room == ctx.stage.rooms[-1]:
      return []

    topleft_pos = ctx.stage_view.camera.rect.topleft
    topleft_cell = vector.floor(
      vector.scale(topleft_pos, 1 / TILE_SIZE)
    )
    left_col, top_row = topleft_cell
    cols = WINDOW_WIDTH // TILE_SIZE + 2
    rows = WINDOW_HEIGHT // TILE_SIZE + 2

    room_cells = room.cells
    if not ctx.stage.is_overworld:
      room_cells = [c for c in room_cells
        if ctx.stage.is_cell_walkable(c)]

    grid_cells = [(x, y)
      for y in range(top_row, top_row + rows)
      for x in range(left_col, left_col + cols)
          if (x, y) in room_cells]

    GRID_CELL_ELEV = 16

    render_grid_cell = lambda image, cell: (
      will_anim := next((a for g in ctx.stage_view.anims for a in g
        if isinstance(a, CombatGridCellAnim) and a.target == cell), None),
      cell_anim := will_anim
        if will_anim in (ctx.stage_view.anims[0] if ctx.stage_view.anims else [])
        else None,
      cell_anim_pos := (ease_out(cell_anim.pos)
        if isinstance(cell_anim, CombatGridCellEnterAnim)
        else 1 - cell_anim.pos)
          if cell_anim and cell_anim.time >= 0
          else inf if (not ctx.exiting and cell_anim or ctx.exiting and not will_anim) else 1,
      cell_offset := (-1 + cell_anim_pos) * GRID_CELL_ELEV,
      Sprite(
        image=image,
        pos=vector.subtract(
          vector.add(
            tuple([x * TILE_SIZE for x in cell]),
            (cell_offset, TILE_SIZE + cell_offset)
          ),
          topleft_pos,
        ),
        layer="markers",
        origin=Sprite.ORIGIN_BOTTOMLEFT,
        target=cell,
      ) if cell_offset != inf
          and not (cell_anim and cell_anim.time % 2)
          and not (not ctx.exiting and not cell_anim and will_anim)
        else None
    )[-1]

    return [cell_sprite for cell in grid_cells if (cell_sprite := render_grid_cell(
      image=assets.sprites["combat_grid_cell"],
      cell=cell,
    ))]
