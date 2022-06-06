from lib.sequence import play_sequence, stop_sequence
import lib.vector as vector
from lib.cell import upscale
from contexts.cutscene import CutsceneContext
from dungeon.props.column import Column
from dungeon.hooks.shrine.magestruggle import sequence_mage_struggle
from anims.pause import PauseAnim

import config
from config import TILE_SIZE

def on_focus(room, game):
  altar = room.altar = game.stage.find_elem(cls="Altar")
  mage = room.mage = game.stage.find_elem(cls="Mage")
  hero = game.hero
  mage_struggle = sequence_mage_struggle(room, game)

  if "minxia" in game.store.story:
    column = next((e for e in game.stage.elems if type(e) is Column and e.cell[0] > altar.cell[0] + 3), None)
    column and game.stage.remove_elem(column)

  if "minxia" in game.store.story or not config.CUTSCENES:
    game.stage.remove_elem(mage)
    room.mage = None
    return

  game.get_tail().open(CutsceneContext(script=[
    lambda step: (
      game.anims.append([PauseAnim(
        duration=1,
        on_end=lambda: (
          game.camera.blur(hero),
          game.camera.focus(
            upscale(vector.add(altar.cell, (0, 1)), TILE_SIZE),
            instant=True
          ),
          step()
        )
      )])
    ),
    *(mage_struggle * 2),
    lambda step: (
      play_sequence(mage_struggle),
      game.camera.tween(
        target=upscale(hero.cell, TILE_SIZE),
        duration=150,
        on_end=lambda: (
          stop_sequence(mage_struggle),
          step()
        )
      )
    ),
    lambda step: (
      game.camera.focus(
        target=[room, hero],
        force=True
      ),
      step(),
    )
  ]))
