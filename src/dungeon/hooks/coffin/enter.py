from math import inf

from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
import lib.vector as vector
from lib.cell import upscale

from dungeon.actors.mummy import Mummy
from dungeon.props.coffin import Coffin
from anims.pause import PauseAnim
from anims.shake import ShakeAnim
from anims.jump import JumpAnim
from anims.step import StepAnim
from anims.path import PathAnim
from anims.attack import AttackAnim
from anims.warpin import WarpInAnim
from vfx.alertbubble import AlertBubble

import config
from config import PUSH_DURATION, RUN_DURATION, NUDGE_DURATION

def on_enter(room, game):
  room.mage = game.stage.find_elem(cls="Mage")
  game.get_tail().open(CutsceneContext([
    *(cutscene(room, game) if (config.CUTSCENES and "minxia" not in game.store.story) else [
      game.stage.remove_elem(room.mage),
      setattr(room, "mage", None),
      *take_battle_position(room, game),
      lambda step: (
        spawn_enemies(room, game),
        room.lock(game),
        step(),
      ),
      lambda step: (
        game.handle_combat(),
        game.camera.focus(
          target=[room, game.hero],
          force=True
        ),
        step(),
      )
    ])
  ]))

def cutscene(room, game):
  hero = game.hero
  mage = room.mage
  for door in room.get_doors(game.stage):
    door.open()
  return [
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.vfx.append(AlertBubble(hero.cell)),
      game.anims.append([PauseAnim(duration=45, on_end=step)]),
    ),
    *take_battle_position(room, game),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.get_tail().open(DialogueContext(script=[
        lambda: game.anims.append([ShakeAnim(target=mage, duration=15)]),
        (hero.name.upper(), "You sure like running, don't you?"),
        lambda: game.anims.append([JumpAnim(target=mage)]),
        (mage.name.upper(), "Ack!"),
      ]), on_close=step)
    ),
    lambda step: (
      setattr(mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)]),
    ),
    lambda step: (
      setattr(mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)]),
    ),
    lambda step: (
      game.get_tail().open(DialogueContext(script=[
        (mage.name.upper(), "Ugh, you AGAIN?"),
        lambda: (
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.CheekyAnim())
        ) and (mage.name.upper(), "Look, I already spent all your little coins on jewelry and makeup."),
        (mage.name.upper(), "You don't have a reason to chase me!"),
        lambda: (
          game.anims.append([StepAnim(
            target=hero,
            duration=PUSH_DURATION,
            src=hero.cell,
            dest=vector.add(hero.cell, hero.facing),
          )]),
          hero.move_to(vector.add(hero.cell, hero.facing))
        ) and (hero.name.upper(), "Give me my sword."),
        lambda: (
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.LaughAnim())
        ) and (mage.name.upper(), "Hee hee hee..."),
        lambda: (
          mage.core.anims.clear(),
          game.anims.append([StepAnim(target=mage, duration=inf, period=30)])
        ) and (mage.name.upper(), "How about I keep it, and you deal with whatever nice fellas might be in here?"),
        (hero.name.upper(), "????"),
        lambda: (
          game.anims.clear(),
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.CastAnim())
        ) and (mage.name.upper(), "SUPER...."),
        (mage.name.upper(), "YELLING..."),
        (mage.name.upper(), "ATTACK!!!"),
        lambda: (
          setattr(mage, "facing", (-1, 0)),
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.YellAnim()),
          game.anims.append([
            ShakeAnim(target=mage, magnitude=0.5),
            StepAnim(
              target=hero,
              duration=NUDGE_DURATION,
              src=hero.cell,
              dest=vector.add(hero.cell, (0, 1)),
            )
          ]),
          game.vfx.append(AlertBubble(hero.cell)),
          hero.move_to(vector.add(hero.cell, (0, 1)))
        ) and (mage.name.upper(), "AAAAAHHH!!!!!!!!!"),
      ]), on_close=step),
    ),
    lambda step: (
      game.camera.tween(
        target=upscale(vector.add(room.get_center(), (0, 0.5)), game.stage.tile_size),
        on_end=step
      ),
    ),
    lambda step: (
      game.stage_view.shake(duration=inf, vertical=True),
      setattr(hero, "facing", (-1, 0)),
      game.get_tail().open(DialogueContext(script=[
        spawn_enemies(room, game) and ("????", "Urrrrrgh....."),
        lambda: (
          setattr(hero, "facing", (0, -1)),
          game.anims[0].append(JumpAnim(target=hero)),
        ) and (hero.name.upper(), "You idiot! You're gonna get us both killed!")
      ]), on_close=step)
    ),
    lambda step: (
      game.anims.clear(),
      mage.core.anims.clear(),
      setattr(mage, "facing", (0, 1)),
      game.anims.append([StepAnim(target=mage, duration=inf, period=30)]),
      game.camera.tween(
        target=upscale(vector.add(room.get_center(), (0, -room.get_height() // 2 + 2)), game.stage.tile_size),
        on_end=step
      ),
    ),
    lambda step: (
      game.get_tail().open(DialogueContext(script=[
        (mage.name.upper(), "If someone's gonna kick the bucket down here,"),
        (mage.name.upper(), "it's not gonna be me!"),
        (hero.name.upper(), "!!"),
      ]), on_close=step),
    ),
    lambda step: (
      goal_cell := sorted(room.edges, key=lambda e: e[1])[0],
      game.anims.clear(),
      game.anims.append([PathAnim(
        target=mage,
        period=RUN_DURATION,
        path=game.stage.pathfind(
          start=mage.cell,
          goal=goal_cell,
          whitelist=room.cells + room.edges
        ),
        on_end=lambda: (
          mage.move_to(goal_cell),
          step()
        )
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
    lambda step: (
      setattr(mage, "facing", (-1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: (
      setattr(mage, "facing", (0, -1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: (
      setattr(mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: (
      setattr(mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: (
      game.get_tail().open(DialogueContext(script=[
        (mage.name.upper(), "So long, suckers!"),
        (mage.name.upper(), "Don't make too much of a mess, you hear?"),
      ]), on_close=step),
    ),
    lambda step: game.anims.append([PathAnim(
      target=mage,
      period=RUN_DURATION,
      path=[vector.add(room.cell, (room.get_width() // 2, -1), c) for c in [(0, 0), (0, -1)]],
      on_end=lambda: (
        game.stage.remove_elem(mage),
        step()
      )
    )]),
    lambda step: (
      game.get_tail().open(DialogueContext(script=[
        lambda: game.anims.append([ShakeAnim(target=hero, duration=30)]),
        (hero.name.upper(), "H-hey!"),
      ]), on_close=step)
    ),
    lambda step: (
      goal_cell := vector.add(sorted(room.edges, key=lambda e: e[1])[0], (0, 1)),
      game.anims.clear(),
      game.anims.append([PathAnim(
        target=hero,
        period=RUN_DURATION,
        path=game.stage.pathfind(start=hero.cell, goal=goal_cell),
        on_end=step
      ), PauseAnim(
        duration=45,
        on_end=lambda: room.lock(game)
      )]),
    ),
    lambda step: (
      game.anims.append([AttackAnim(
        target=hero,
        src=hero.cell,
        dest=vector.add(hero.cell, (0, -1)),
        on_start=lambda: setattr(hero, "facing", (0, -1)),
        on_end=step
      )])
    ),
    lambda step: (
      game.anims.append([AttackAnim(
        target=hero,
        src=hero.cell,
        dest=vector.add(hero.cell, (0, -1)),
        on_end=step
      )])
    ),
    lambda step: (
      game.get_tail().open(DialogueContext(script=[
        lambda: (
          setattr(hero, "facing", (-1, 0)),
          game.anims.append([JumpAnim(target=hero)])
        ) and (hero.name.upper(), "Damn! That mousy little...!"),
        lambda: (
          setattr(hero, "facing", (0, 1))
        ) or (hero.name.upper(), "Looks like I'll have to put these guys back to sleep first!"),
        lambda: (
          game.stage_view.unshake(),
        ) and None
      ]), on_close=step)
    ),
    lambda step: (
      game.handle_combat(),
      game.camera.focus(target=[room, hero], force=True),
      step(),
    )
  ]

def take_battle_position(room, game):
  hero = game.hero
  mage = room.mage if not game.ally else None
  goal_cell = (mage
    and vector.add(mage.cell, (0, 2))
    or vector.add(sorted(room.edges, key=lambda e: e[1])[0], (0, 1)))
  return [
    lambda step: (
      game.anims.append([PathAnim(
        target=hero,
        path=game.stage.pathfind(
          start=hero.cell,
          goal=goal_cell
        ),
        on_end=lambda: (
          hero.stop_move(),
          step(),
        )
      )]),
      game.ally and game.anims[-1].append(PathAnim(
        target=game.ally,
        path=[vector.add(c, (0, 1)) for c in game.anims[-1][-1].path],
        on_end=lambda: (
          game.ally.stop_move(),
        )
      )),
    ),
  ]

def spawn_enemies(room, game):
  return [
    (
      game.stage.spawn_elem_at(c.cell, mummy := Mummy(aggro=3)),
      not game.anims and game.anims.append([]),
      game.anims[0].append(WarpInAnim(
        target=mummy,
        duration=15,
        delay=i * 8,
        on_start=c.open
      ))
    ) for i, c in enumerate([
      e for c in room.cells
        for e in game.stage.get_elems_at(c)
          if isinstance(e, Coffin)
    ]) if i in (0, 3, 4)
  ]
