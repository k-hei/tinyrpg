from lib.cell import add as add_vector, upscale
import lib.vector as vector
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from helpers.combat import animate_snap
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.path import PathAnim
from anims.pause import PauseAnim
from anims.shake import ShakeAnim
import config

def on_enter(room, game):
  if "minxia" in game.store.story:
    return False

  game.open(CutsceneContext(script=[
    *prebattle_cutscene_setup(room, game),
    *(prebattle_cutscene(room, game) if config.CUTSCENES else []),
    *prebattle_cutscene_teardown(room, game),
  ]))
  return True

def prebattle_cutscene_setup(room, game):
  mage = room.mage
  room.lock(game)
  return [
    lambda step: animate_snap(
      actor=game.hero,
      anims=game.anims,
      on_end=step,
    ),
    lambda step: game.anims.append([PauseAnim(
      duration=30,
      on_end=step,
    )]),
    lambda step: (
      game.camera.focus(
        target=upscale(vector.add(mage.cell, (0, 1)), game.stage.tile_size),
        force=True
      ),
      game.anims.append([PathAnim(
        target=game.hero,
        path=game.stage.pathfind(
          start=game.hero.cell,
          goal=vector.add(mage.cell, (0, 2)),
          whitelist=room.cells,
        ),
        on_end=step
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      setattr(room.mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
  ]

def prebattle_cutscene(room, game):
  knight = game.hero
  mage = room.mage
  return [
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.get_tail().open(DialogueContext(script=[
      (mage.name, "Won't you just stay dead and gone already!"),
      lambda: game.anims.append([JumpAnim(target=knight)]),
      (knight.name, "Give me back my money! And my sword!"),
      (knight.name, "And apologize for the inconveniences you have caused!"),
    ]), on_close=step),
    lambda step: game.anims.append([AttackAnim(
      target=mage,
      src=mage.cell,
      dest=add_vector(mage.cell, mage.facing),
      on_end=step
    )]),
    lambda step: game.get_tail().open(DialogueContext(script=[
      (mage.name, "I'm NOT sorry I took those treasures."),
      (mage.name, "I need them more than you!"),
      lambda: game.anims.extend([
        [PauseAnim(duration=5)],
        [PathAnim(
          target=mage,
          path=[
            mage.cell,
            vector.add(mage.cell, (-1, 0)),
            mage.cell,
            vector.add(mage.cell, (1, 0)),
            mage.cell,
          ],
        )],
        [JumpAnim(
          target=mage,
          on_end=lambda: mage.face(knight.cell),
        )]
      ]),
      (mage.name, "Do you know the last time I had a piece of cheese? OR BREAD?"),
    ]), on_close=step),
    lambda step: game.anims.append([ShakeAnim(target=knight, duration=30, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.get_tail().open(DialogueContext(script=[
      (knight.name, "You did far more than just that!"),
      (mage.name, "Why don't you leave me alone already!"),
      (mage.name, "I'm not interested in being a captive of anyone else's again!"),
    ]), on_close=step),
    lambda step: game.anims.append([AttackAnim(
      target=knight,
      src=knight.cell,
      dest=add_vector(knight.cell, knight.facing),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.get_tail().open(DialogueContext(script=[
      (knight.name, "Not only have you been trying to put me in the ground,"),
      (knight.name, "you're permitless and exploring a tomb without permission."),
      (knight.name, "A few years in a little box will give you enough time to think about everything you've done."),
    ]), on_close=step),
    lambda step: (
      setattr(room.mage, "facing", (-1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, -1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.get_tail().open(DialogueContext(script=[
      (mage.name, "Come and get me then, tin man!!"),
    ]), on_close=step),
  ]

def prebattle_cutscene_teardown(room, game):
  mage = room.mage
  return [
    lambda step: (
      game.anims.append([PathAnim(
        target=mage,
        path=[
          mage.cell,
          vector.add(mage.cell, (0, -1)),
        ],
        on_end=step
      )])
    ),
    lambda step: (
      setattr(room.mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      setattr(mage, "faction", "enemy"),
      game.handle_combat(),
      game.anims[0].extend(mage.animate_brandish(on_end=step)),
      step(),
    ),
    lambda step: game.anims.append([PauseAnim(duration=45, on_end=step)]),
    lambda step: (
      game.camera.blur(),
      step(),
    )
  ]
