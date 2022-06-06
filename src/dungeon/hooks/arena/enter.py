from lib.cell import upscale
from contexts.cutscene import CutsceneContext
from anims.pause import PauseAnim
from anims.jump import JumpAnim
from anims.awaken import AwakenAnim
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.mummy import Mummy
import config

def on_enter(room, game):
  room.waves = [
    # [Eyeball, Mushroom, Mushroom, Mummy],
  ]

  room.lock(game)
  eyeballs = [e for c in room.cells for e in game.stage.get_elems_at(c) if isinstance(e, Eyeball)]
  eyeballs.sort(key=lambda e: (
    0 if e.rare
    else 1 if not e.ailment == "sleep"
    else 2
  ))

  if not config.CUTSCENES:
    for eyeball in eyeballs:
      eyeball.alert(cell=game.hero.cell)
    return

  game.get_tail().open(CutsceneContext([
    lambda step: (
      setattr(eyeballs[0], "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: (
      game.camera.focus(
        target=upscale(room.center, game.stage.tile_size),
        force=True
      ),
      game.anims.append([PauseAnim(duration=90, on_end=step)])
    ),
    lambda step: game.anims.extend([
      [PauseAnim(
        duration=30,
        on_start=lambda: setattr(eyeballs[0], "facing", (0, 1))
      )],
      [JumpAnim(
        target=eyeballs[0],
        on_start=lambda: setattr(eyeballs[0], "aggro", 1)
      )],
      [PauseAnim(duration=5)],
      [JumpAnim(
        target=eyeballs[0],
        on_end=step
      )]
    ]),
    lambda step: game.anims.extend([
      [PauseAnim(duration=15)],
      [AwakenAnim(
        target=eyeballs[2],
        duration=30,
        on_start=lambda: (
          eyeballs[2].dispel_ailment(),
          setattr(eyeballs[2], "aggro", 1),
          setattr(eyeballs[1], "facing", (-1, 0)),
        ),
        on_end=lambda: (
          setattr(eyeballs[1], "facing", (0, 1)),
          setattr(eyeballs[1], "aggro", 1),
        )
      )],
      [PauseAnim(duration=30, on_end=step)]
    ]),
    lambda step: (
      game.camera.blur(),
      game.handle_combat(),
      step()
    )
  ]))
