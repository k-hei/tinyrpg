import lib.vector as vector
from lib.cell import upscale
from lib.sequence import play_sequence, stop_sequence
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from dungeon.hooks.shrine.magestruggle import sequence_mage_struggle
from dungeon.hooks.shrine.magespin import sequence_mage_spin
from dungeon.hooks.shrine.magebump import sequence_mage_bump
from anims.step import StepAnim
from anims.jump import JumpAnim
from anims.shake import ShakeAnim
from anims.pause import PauseAnim
import config

def on_walk(room, game, cell):
  if cell == vector.add(room.altar.cell, (0, 4)):
    trigger_cutscene(room, game)

def trigger_cutscene(room, game):
  altar = room.altar
  mage = room.mage
  hero = game.hero
  mage_struggle = sequence_mage_struggle(room, game)
  mage_spin = sequence_mage_spin(room, game)
  mage_bump = sequence_mage_bump(room, game)
  if "minxia" in game.store.story or not config.CUTSCENES:
    return
  game.get_tail().open(cutscene := CutsceneContext([
    lambda step: (
      hero.stop_move(),
      game.anims.append([PauseAnim(duration=30, on_end=step)]),
      play_sequence(mage_struggle)
    ),
    lambda step: (
      game.camera.tween(
        target=upscale(vector.add(altar.cell, (0, 1.5)), game.stage.tile_size),
        duration=60,
        on_end=step
      )
    ),
    lambda step: game.get_tail().open(DialogueContext([
      (mage.name, "There's gotta be..."),
      (mage.name, "a button..."),
      (mage.name, "to open this darn thing..."),
      (mage.name, "somewhere!"),
      lambda: stop_sequence(mage_struggle),
      lambda: setattr(mage, "cell", vector.add(altar.cell, (-1, 0))),
      lambda: setattr(mage, "facing", (1, 0)),
      lambda: game.anims.append([
        ShakeAnim(target=mage, duration=30),
        StepAnim(
          target=hero,
          src=hero.cell,
          dest=(hero_dest := vector.add(altar.cell, (0, 2))),
          on_end=lambda: setattr(hero, "cell", hero_dest)
        )
      ]),
      (hero.name, "HOLD IT, MISSY!"),
      lambda: game.anims.append([JumpAnim(target=mage)]),
      lambda: play_sequence(mage_spin),
      (mage.name, "EEP! I'm done for!!"),
      (hero.name, "Do you have the proper permit to explore this tomb??"),
      lambda: stop_sequence(mage_spin),
      lambda: setattr(mage, "facing", (-1, 0)),
      lambda: game.anims.extend([
        [PauseAnim(
          duration=30,
          on_end=lambda: setattr(mage, "facing", (0, 1)),
        )],
        [ShakeAnim(target=mage, duration=15)]
      ]),
      (mage.name, "P-permit?!"),
      lambda: mage.core.anims.append(mage.core.ThinkAnim()),
      (mage.name, "Hey, you're not one of those slavers..."),
      lambda: game.anims.append([JumpAnim(target=hero)]),
      (hero.name, "You need a permit to explore here!"),
      lambda: mage.core.anims.clear(),
      lambda: game.anims.append([JumpAnim(target=mage)]),
      lambda: game.anims.extend([
        [PauseAnim(duration=30, on_end=lambda: setattr(mage, "facing", (1, 0)))],
        [PauseAnim(duration=30, on_end=lambda: play_sequence(mage_bump))]
      ]),
      (mage.name, "Hey, stickwad, I'm just looking for a place to hide from those cretins outside!"),
      (mage.name, "Just let me crawl in this box and be on your damn way!"),
      lambda: game.anims.append([PauseAnim(
        duration=5,
        on_end=lambda: stop_sequence(mage_bump)
      )]),
      lambda: game.anims.append([
        ShakeAnim(target=hero, duration=30)
      ]),
      (hero.name, "Don't open that! You don't know what could-"),
    ]), on_close=step),
    lambda step: game.anims.append([PauseAnim(duration=5, on_end=step)]),
    lambda step: (
      cutscene.script.extend(altar.effect(game)),
      step(),
    ),
  ]))
