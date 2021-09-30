from lib.sequence import play_sequence, stop_sequence
import lib.vector as vector
from contexts.cutscene import CutsceneContext
from dungeon.props.column import Column
from dungeon.hooks.shrine.magestruggle import sequence_mage_struggle
import config

def on_focus(room, game):
  altar = room.altar = game.floor.find_elem(cls="Altar")
  mage = room.mage = game.floor.find_elem(cls="Mage")
  hero = game.hero
  mage_struggle = sequence_mage_struggle(room, game)

  if "minxia" in game.store.story:
    column = next((e for e in game.floor.elems if type(e) is Column and e.cell[0] > altar.cell[0] + 3), None)
    column and game.floor.remove_elem(column)

  if "minxia" in game.store.story or not config.CUTSCENES:
    game.floor.remove_elem(mage)
    room.mage = None
    return

  game.open(CutsceneContext(script=[
    lambda step: (
      game.camera.focus(
        cell=vector.add(altar.cell, (0, 1)),
        force=True,
        tween=True,
        speed=1,
      ),
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
