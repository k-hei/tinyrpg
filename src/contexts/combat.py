from random import random, randint
import lib.vector as vector
import lib.input as input
from lib.direction import invert as invert_direction, normal as normalize_direction
from lib.compose import compose
from lib.cell import neighborhood, manhattan, is_adjacent, upscale

from contexts.explore.base import ExploreBase
from contexts.skill import SkillContext
from contexts.gameover import GameOverContext
from contexts.ally import AllyContext
from comps.damage import DamageValue
from dungeon.actors import DungeonActor
from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage
from dungeon.props.door import Door
from skills.weapon import Weapon
from tiles import Tile
import tiles.default as tileset
from anims.move import MoveAnim
from anims.step import StepAnim
from anims.path import PathAnim
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from vfx.flash import FlashVfx
from colors.palette import RED, GREEN, BLUE, GOLD, PURPLE, CYAN
from config import (
  MOVE_DURATION, FLINCH_PAUSE_DURATION, FLICKER_DURATION, NUDGE_DURATION, SIDESTEP_DURATION, SIDESTEP_AMPLITUDE,
  HIT_CHANCE, CRIT_CHANCE, CRIT_MODIFIER,
  TILE_SIZE,
)

COMMAND_MOVE = "move"
COMMAND_MOVE_TO = "move_to"
COMMAND_ATTACK = "attack"
COMMAND_SKILL = "use_skill"
COMMAND_WAIT = "wait"

def find_damage_text(damage):
  if damage == 0:
    return "BLOCK"
  elif damage == None:
    return "MISS"
  else:
    return int(damage)

class CombatContext(ExploreBase):
  def __init__(ctx, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.exiting = False
    ctx.turns = 0
    ctx.command_queue = []
    ctx.command_pending = None
    ctx.command_gen = None
    ctx.busy = False

  def enter(ctx):
    if not ctx.hero:
      return

    downscale = lambda pos: tuple([int(x / ctx.hero.scale) for x in pos])
    upscale = lambda cell: vector.scale(
      vector.add(cell, (0.5, 0.5)),
      ctx.hero.scale
    )

    walk_speed = 3 if ctx.ally else 2
    actor_cells = {}

    def animate_snap(actor, on_end=None):
      x, y = actor.pos
      if x % actor.scale or y % actor.scale:
        actor_cell = downscale(vector.add(
          actor.pos,
          vector.scale(actor.facing, TILE_SIZE / 2)
        ))
        actor_cells[actor] = actor_cell
        actor_dest = upscale(actor_cell)
        actor.stop_move()
        not ctx.anims and ctx.anims.append([])
        ctx.anims[-1].append(MoveAnim(
          target=actor,
          src=actor.pos,
          dest=actor_dest,
          speed=walk_speed,
          on_end=on_end
        ))

    create_brandish = lambda actor: (
      actor.core.BrandishAnim(
        target=actor,
        on_start=(lambda: (
          ctx.anims[0].append(JumpAnim(
            target=actor,
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

    hero_brandish = create_brandish(ctx.hero)

    animate_snap(ctx.hero, on_end=(lambda: (
      ctx.anims[0].append(hero_brandish)
    )) if not ctx.ally else None)
    ctx.ally and animate_snap(ctx.ally)

    if ctx.ally:
      start_cells = [c for c in neighborhood(ctx.hero.cell, diagonals=True) + [ctx.hero.cell] if
        not next((e for e in ctx.stage.get_elems_at(c) if
          isinstance(e, Door)
          or e.solid and e is not ctx.hero
        ), None)
        and not ctx.stage.is_tile_solid(c)
      ]

      ctx.anims.append([
        PathAnim(
          target=ctx.hero,
          path=ctx.stage.pathfind(
            start=actor_cells[ctx.hero],
            goal=start_cells.pop(0),
            whitelist=ctx.stage.find_walkable_room_cells(room=ctx.room, ignore_actors=True)
          ),
          period=TILE_SIZE // walk_speed,
          on_end=lambda: ctx.anims[0].append(hero_brandish)
        ), PathAnim(
          target=ctx.ally,
          path=ctx.stage.pathfind(
            start=actor_cells[ctx.ally],
            goal=start_cells.pop(0),
            whitelist=ctx.stage.find_walkable_room_cells(room=ctx.room, ignore_actors=True) + [ctx.ally.cell]
          ),
          period=TILE_SIZE // walk_speed,
          on_end=lambda: ctx.anims[0].append(ally_brandish)
        )
      ])

      ally_brandish = create_brandish(ctx.ally)

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
      ctx.anims.append([PathAnim(
        target=ctx.ally,
        period=TILE_SIZE / 3,
        path=ctx.stage.pathfind(
          start=ctx.ally.cell,
          goal=target_cell,
          whitelist=ctx.stage.find_walkable_room_cells(room=ctx.room, ignore_actors=True)
        )
      )])

    ctx.exiting = True
    ctx.comps.sp_meter.exit()
    ctx.comps.hud.exit(on_end=lambda: (
      ctx.hero.core.anims.clear(),
      ctx.ally and ctx.ally.core.anims.clear(),
      ctx.close()
    ))

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.anims or ctx.exiting:
      return

    delta = input.resolve_delta(button, fixed_axis=True)
    if delta != (0, 0):
      return ctx.handle_move(delta)

    tapping = input.get_state(button) == 1
    control = input.resolve_control(button)

    if control == input.CONTROL_CONFIRM:
      return ctx.handle_action()

    if control == input.CONTROL_WAIT and tapping:
      return ctx.handle_wait()

    if control == input.CONTROL_MANAGE and tapping:
      return ctx.handle_skill()

    if control == input.CONTROL_ALLY and input.get_state(button) > 15:
      return ctx.handle_charmenu()

  def handle_release(ctx, button):
    if ctx.child:
      return ctx.child.handle_release(button)

    control = input.resolve_control(button)
    if control == input.CONTROL_ALLY and input.get_state(button) <= 15:
      return ctx.handle_charswap()

  def handle_move(ctx, delta):
    target_cell = vector.add(ctx.hero.cell, delta)
    target_tile = ctx.stage.get_tile_at(target_cell)

    def on_move():
      target_elem = next((e for e in ctx.stage.get_elems_at(ctx.hero.cell) if not isinstance(e, DungeonActor)), None)
      target_elem and target_elem.effect(ctx, ctx.hero)

    ctx.hero.facing = delta
    moved = ctx.move(ctx.hero, delta, on_end=on_move)
    if not moved and issubclass(target_tile, tileset.Pit):
      moved = ctx.leap(actor=ctx.hero, on_end=on_move)

    moved and ctx.step()
    return moved

  def move(ctx, actor, delta, jump=False, on_end=None):
    target_cell = vector.add(actor.cell, delta)
    target_tile = ctx.stage.get_tile_at(target_cell)
    if not Tile.is_walkable(target_tile):
      return False

    target_elem = (
      next((e for e in ctx.stage.get_elems_at(target_cell) if e.solid), None)
      or next((e for e in ctx.stage.get_elems_at(target_cell)), None)
    )

    if target_elem and target_elem.solid and not (target_elem is ctx.ally and not ctx.ally.command):
      return False

    move_command = (actor, (COMMAND_MOVE, delta))
    ctx.command_queue.append(move_command)

    move_duration = MOVE_DURATION
    move_duration = move_duration * 1.5 if jump else move_duration
    move_kind = JumpAnim if jump else StepAnim
    move_anim = move_kind(
      target=actor,
      src=actor.cell,
      dest=target_cell,
      duration=move_duration,
      on_end=lambda: (
        move_command in ctx.command_queue and ctx.command_queue.remove(move_command),
        ctx.update_bubble(),
        on_end and on_end(),
      )
    )
    move_anim.update() # initial update to ensure walk animation loops seamlessly

    move_group = next((g for g in ctx.anims for a in g if isinstance(a, StepAnim) and isinstance(a.target, DungeonActor)), None)
    not move_group and ctx.anims.append(move_group := [])
    move_group.append(move_anim)
    if jump:
      ctx.anims[-1].append(PauseAnim(duration=move_duration + 5))

    ctx.update_bubble()
    actor.cell = target_cell
    actor.facing = normalize_direction(delta)
    actor.command = move_command

    if target_elem and target_elem is ctx.ally:
      ctx.move(actor=ctx.ally, delta=invert_direction(delta))

    return True

  def move_to(ctx, actor, dest, run=False, on_end=None):
    if actor.cell == dest or actor.ai_path and actor.cell == actor.ai_path[-1]:
      actor.ai_path = None
      if actor.cell == actor.ai_target:
        actor.ai_mode = DungeonActor.AI_LOOK
        actor.aggro = 0
      elif actor.cell == dest:
        on_end and on_end()
        return False

    if not actor.ai_path:
      actor.ai_path = ctx.stage.pathfind(
        start=actor.cell,
        goal=dest,
        whitelist=ctx.stage.find_walkable_room_cells(cell=actor.cell, ignore_actors=True)
      )

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
      moved = ctx.move(actor, delta, run, on_end=on_end)

    if not moved:
      actor.ai_path = ctx.stage.pathfind(start=actor.cell, goal=dest)
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
    delta = vector.scale(actor.facing, 2)
    moved = ctx.move(actor, delta, jump=True, on_end=on_end)
    return moved

  def handle_action(ctx):
    facing_actor = ctx.facing_actor
    if isinstance(facing_actor, DungeonActor) and facing_actor.faction == "enemy":
      return ctx.handle_attack()

    facing_elem = ctx.facing_elem
    action_result = facing_elem.effect(ctx, ctx.hero) if facing_elem else False
    if action_result != None:
      not ctx.anims and ctx.anims.append([])
      ctx.anims[0].insert(0, AttackAnim(
        target=ctx.hero,
        src=ctx.hero.cell,
        dest=vector.add(ctx.hero.cell, ctx.hero.facing),
      ))
      ctx.update_bubble()

    return action_result

  def handle_attack(ctx):
    target_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    target_actor = next((e for e in ctx.stage.get_elems_at(target_cell) if isinstance(e, DungeonActor)), None)
    ctx.store.sp -= 1
    return ctx.attack(actor=ctx.hero, target=target_actor, on_end=ctx.step)

  def attack(ctx, actor, target=None, modifier=1, animate=True, on_end=None):
    if target:
      actor.face(target.cell)
      crit = ctx.find_crit(actor, target)
      miss = ctx.find_miss(actor, target)
      if miss:
        damage = None
      elif crit:
        damage = ctx.find_damage(actor, target, modifier=modifier * CRIT_MODIFIER)
      else:
        damage = ctx.find_damage(actor, target, modifier)

    attack_command = (actor, (COMMAND_ATTACK, target))
    ctx.command_queue.append(attack_command)

    connect = lambda: (
      target.alert(cell=actor.cell),
      ctx.flinch(
        target=target,
        damage=damage,
        crit=crit,
        direction=actor.facing,
        on_end=lambda: (
          attack_command in ctx.command_queue and ctx.command_queue.remove(attack_command),
          on_end and on_end()
        ),
      )
    )

    if animate:
      attack_delay = (
        actor.core.AttackAnim.frames_duration[0]
          if "AttackAnim" in dir(actor.core) and actor.facing == (0, 1)
          else 0
      )
      ctx.anims.extend([
        [*([PauseAnim(
          duration=attack_delay,
          on_start=lambda: actor.attack()
        )] if attack_delay else [])],
        [AttackAnim(
          target=actor,
          src=actor.cell,
          dest=vector.add(actor.cell, actor.facing),
          on_connect=(connect if target else None)
        )]
      ])
    else:
      connect()

    return True

  def find_damage(ctx, actor, target, modifier=1):
    actor_st = actor.st * modifier
    target_en = target.en
    variance = 1
    return max(1, actor_st - target_en + randint(-variance, variance))

  def find_miss(ctx, actor, target):
    return (
      not target.is_immobile()
      and target.facing != actor.facing
      and (target.aggro > 1 or target.faction == "player")
      and not ctx.roll_hit(attacker=actor, defender=target)
    )

  def find_crit(ctx, actor, target):
    return target.ailment != DungeonActor.AILMENT_FREEZE and (
      target.ailment == DungeonActor.AILMENT_SLEEP
      or actor.facing == target.facing
      or ctx.roll_crit(attacker=actor, defender=target)
    )

  def roll(game, dx, ag, chance):
    if dx >= ag:
      chance = chance + (dx - ag) / 100
    elif ag >= dx * 2:
      chance = dx / ag * chance * 0.75
    else:
      chance = dx / ag * chance
    return random() <= chance

  def roll_hit(ctx, attacker, defender):
    return ctx.roll(
      dx=attacker.stats.dx + attacker.stats.lu / 2,
      ag=defender.stats.ag + defender.stats.lu / 2,
      chance=HIT_CHANCE,
    )

  def roll_crit(ctx, attacker, defender):
    return ctx.roll(
      dx=attacker.stats.dx + attacker.stats.lu / 2,
      ag=defender.stats.ag + defender.stats.lu / 2,
      chance=CRIT_CHANCE,
    )

  def flinch(ctx, target, damage, direction=None, crit=False, animate=True, on_end=None):
    show_text = lambda: ctx.vfx.append(DamageValue(
      text=find_damage_text(damage),
      cell=target.cell,
    ))

    if damage and crit:
      ctx.vfx.extend([
        DamageValue(
          text="CRITICAL!",
          cell=target.cell,
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
        if target.is_dead() or issubclass(ctx.stage.get_tile_at(target.cell), tileset.Pit)
        else on_end and on_end()
    )

    if animate:
      anim_group = next((g for g in ctx.anims if not next((a for a in g if a.target is target), None)), [])
      anim_group not in ctx.anims and ctx.anims.append(anim_group)
      anim_group.extend([
        *([FlinchAnim(
          target=target,
          direction=direction,
          on_start=inflict
        )] if damage is not None else [AttackAnim(
          target=target,
          src=target.cell,
          dest=vector.add(target.cell, vector.tangent(direction)),
          duration=SIDESTEP_DURATION,
          amplitude=SIDESTEP_AMPLITUDE,
        )] if direction else []),
        PauseAnim(
          duration=FLINCH_PAUSE_DURATION,
          on_end=cleanup
        )
      ])
      not damage and inflict()
    else:
      inflict()
      cleanup()

  def nudge(ctx, actor, direction, on_end=None):
    source_cell = actor.cell
    target_cell = vector.add(source_cell, direction)
    target_tile = ctx.stage.get_tile_at(target_cell)
    if not ctx.stage.is_cell_empty(target_cell) and not issubclass(target_tile, tileset.Pit):
      return False

    actor.cell = target_cell
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
      if target is ctx.hero:
        if ctx.ally:
          ctx.handle_charswap()
        else:
          ctx.handle_gameover()
      ctx.stage.remove_elem(target)
      will_exit and ctx.exit(ally_rejoin=True)
      on_end and on_end()

    not ctx.anims and ctx.anims.append([])
    ctx.anims[0].append(FlickerAnim(
      target=target,
      duration=FLICKER_DURATION,
      on_end=remove_elem
    ))

  def handle_charswap(ctx):
    if not ctx.ally or ctx.ally.dead:
      ctx.comps.hud.shake()
      return False
    ctx.store.switch_chars()
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
    ctx.comps.hud.exit()
    ctx.open(GameOverContext())

  def handle_skill(ctx):
    ctx.open(SkillContext(
      actor=ctx.hero,
      skills=ctx.hero.get_active_skills(),
      selected_skill=ctx.store.get_selected_skill(ctx.hero.core),
      on_close=lambda skill, dest: (
        skill and (
          not issubclass(skill, Weapon) and ctx.store.set_selected_skill(ctx.hero, skill),
          ctx.use_skill(ctx.hero, skill, dest, on_end=ctx.step),
        )
      )
    ))

  def use_skill(ctx, actor, skill, dest=None, on_end=None):
    if actor.faction == "player":
      ctx.store.sp -= skill.cost

    skill_command = (actor, (COMMAND_SKILL, skill, dest))
    ctx.command_queue.append(skill_command)
    cache_camera_target_count = len(ctx.camera.target_groups)
    skill.effect(
      ctx,
      actor,
      dest,
      on_start=lambda *target: (
        target and ctx.camera.focus(
          target=(
            upscale(target[0], TILE_SIZE)
              if type(target[0]) is tuple
              else target[0]
          ),
          force=True
        ),
        ctx.display_skill(skill, user=actor),
      ),
      on_end=lambda: (
        skill_command in ctx.command_queue and ctx.command_queue.remove(skill_command),
        len(ctx.camera.target_groups) > cache_camera_target_count and ctx.camera.blur(),
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
        cell=actor.cell,
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
      chain = actor.turns > 1
      ctx.command_pending = None
      ctx.step_command(actor, command, chain)

  def step(ctx):
    actors = [e for e in ctx.stage.elems if
      isinstance(e, DungeonActor)
      and e is not ctx.hero
      and e is not ctx.ally
      and not e.is_dead()
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
      if not actor.hp:
        continue

      while actor.turns >= 1:
        actor.turns -= 1

        if actor.charge_turns == 1 and ctx.command_queue:
          yield None

        command = actor.step_charge()

        while not command:
          command = ctx.step_enemy(actor)

          if not command:
            break

          if command[0] in (COMMAND_ATTACK, COMMAND_SKILL) and ctx.command_queue:
            command = None
            yield None

        if command:
          yield actor, command

    ctx.end_step()

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

  def step_enemy(ctx, actor):
    if not actor.can_step():
      return None
    return actor.step(ctx)

  def step_command(ctx, actor, command, chain=False, on_end=None):
    on_end = on_end or (lambda: None)

    command_name, *command_args = command
    if actor.is_immobile():
      return on_end()

    if command_name == COMMAND_MOVE:
      if chain:
        return ctx.move(actor, *command_args, on_end=on_end)
      else:
        ctx.move(actor, *command_args)
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
    ctx.turns += 1

    actors = [e for e in ctx.stage.elems if isinstance(e, DungeonActor)]
    for actor in actors:
      actor.command = None
      ctx.end_turn(actor)

    non_actors = [e for e in ctx.stage.elems if e not in actors]
    for elem in non_actors:
      elem.step(ctx)

    ctx.stage.elems = [e for e in ctx.stage.elems if not e.done]
