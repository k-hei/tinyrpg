from lib.sequence import play_sequence, stop_sequence
import lib.vector as vector
from contexts.cutscene import CutsceneContext
from dungeon.hooks.shrine.magestruggle import sequence_mage_struggle
import config

def on_enter(room, game):
  altar = room.altar = game.floor.find_elem(cls="Altar")
  mage = room.mage = game.floor.find_elem(cls="Mage")
  hero = game.hero
  mage_struggle = sequence_mage_struggle(room, game)
  if not config.CUTSCENES:
    return
  game.open(CutsceneContext(script=[
    lambda step: (
      game.camera.focus(vector.add(altar.cell, (0, 1)), force=True, tween=True),
      step()
    ),
    *(mage_struggle * 2),
    lambda step: (
      play_sequence(mage_struggle),
      game.camera.focus(hero.cell, force=True, tween=True, speed=150, on_end=lambda: (
        stop_sequence(mage_struggle),
        step()
      ))
    ),
  ]))
