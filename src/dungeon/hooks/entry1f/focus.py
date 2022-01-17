import lib.vector as vector
from lib.cell import upscale
from lib.sequence import play_sequence, stop_sequence
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from anims.pause import PauseAnim
from anims.drop import DropAnim
from anims.jump import JumpAnim
from anims.flinch import FlinchAnim
from anims.path import PathAnim
from anims.item import ItemAnim
from anims.attack import AttackAnim
from anims.awaken import AwakenAnim
from vfx.alertbubble import AlertBubble
from dungeon.actors.mage import Mage
from dungeon.hooks.entry1f.magebump import sequence_mage_bump
from skills.weapon.broadsword import BroadSword
import config
from config import RUN_DURATION

def on_focus(room, game):
  if not config.CUTSCENES or "minxia" in game.store.story:
    return False
  hero = game.hero
  mage = room.mage = Mage()
  game.stage.spawn_elem_at(vector.add(room.center, (1, 0)), mage)
  mage_bump = sequence_mage_bump(room, game)
  door = room.get_doors(game.stage)[0]
  game.get_tail().open(CutsceneContext([
    lambda step: (
      game.camera.focus(target=room, force=True),
      game.anims.extend([
        [
          PauseAnim(duration=30),
          DropAnim(target=game.hero, on_end=lambda: game.hero.inflict_ailment("sleep")),
          DropAnim(target=room.mage, delay=45, bounces=0, on_end=step)
        ],
      ])
    ),
    lambda step: (
      game.anims.append([
        JumpAnim(target=room.mage),
        FlinchAnim(target=room.mage)
      ]),
      game.get_tail().open(DialogueContext([
        (mage.name, "OUUCCHH!!!! MY ASS!!!!!"),
        lambda: game.anims.clear(),
        lambda: game.anims.append([
          JumpAnim(target=room.mage),
        ])
      ]), on_close=step)
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(mage, "facing", (1, 0)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(
      duration=30,
      on_start=lambda: setattr(mage, "facing", (0, -1)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(mage, "facing", (1, 0)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(mage, "facing", (0, 1)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(mage, "facing", (-1, 0)),
      on_end=step
    )]),
    lambda step: game.anims.append([JumpAnim(
      target=mage,
      on_start=lambda: game.vfx.append(AlertBubble(cell=room.mage.cell)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
    lambda step: (
      game.anims.append([
        PathAnim(
          target=mage,
          path=(path := game.stage.pathfind(
            start=mage.cell,
            goal=hero.cell,
            whitelist=room.cells
          )[:-1]),
          on_end=lambda: (
            setattr(mage, "cell", path[-1]),
            step()
          )
        )
      ])
    ),
    lambda step: game.anims.append([
      PauseAnim(
        duration=15,
        on_end=lambda: (
          game.camera.focus(
            target=upscale(vector.add(mage.cell, (0, 1)), game.stage.tile_size),
            force=True,
          ),
          step()
        )
      )
    ]),
    lambda step: game.get_tail().open(DialogueContext([
      lambda: play_sequence(mage_bump),
      (mage.name, "...ow..."),
      (mage.name, "oh fug..."),
      (mage.name, "wake up big guy..."),
      lambda: stop_sequence(mage_bump),
    ]), on_close=step),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(mage, "facing", (0, 1)),
      on_end=step
    )]),
    lambda step: game.get_tail().open(DialogueContext([
      (mage.name, "Well... I tried!"),
      lambda: setattr(mage, "facing", (-1, 0)),
      (mage.name, "I don't think he'll be needing all this useful stuff he's carrying."),
      (mage.name, "Life is for the living!"),
    ]), on_close=step),
    lambda step: game.anims.extend([
      [AttackAnim(
        target=room.mage,
        duration=15,
        src=room.mage.cell,
        dest=game.hero.cell,
        on_end=step
      )],
      [ItemAnim(
        target=room.mage,
        duration=15,
        item=BroadSword
      )]
    ]),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: game.anims.append([
      PathAnim(
        target=mage,
        path=(path := game.stage.pathfind(
          start=mage.cell,
          goal=vector.add(door.cell, (0, 1)),
        )),
        period=RUN_DURATION,
        on_end=lambda: (
          game.stage.remove_elem(mage),
          step()
        )
      )
    ]),
    lambda step: (
      game.camera.focus(target=[room, game.hero], force=True),
      step()
    ),
    lambda step: (
      game.hero.dispel_ailment(),
      game.anims.append([AwakenAnim(target=game.hero, duration=30, on_end=step)])
    ),
    lambda step: game.anims.append([JumpAnim(target=game.hero, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(hero, "facing", (1, 0)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(hero, "facing", (-1, 0)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(
      duration=45,
      on_start=lambda: setattr(hero, "facing", (1, 0)),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(
      duration=15,
      on_start=lambda: setattr(hero, "facing", (0, 1)),
      on_end=step
    )]),
  ]))
