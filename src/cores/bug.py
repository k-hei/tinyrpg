from pygame.transform import flip
from cores import Core, Stats
import assets
from sprite import Sprite
from contexts.dialogue import DialogueContext
from anims.move import MoveAnim

class Bug(Core):
  def __init__(bug, name="Buge", faction="ally", *args, **kwargs):
    super().__init__(
      name=name,
      faction=faction,
      stats=Stats(ag=7),
      message=lambda ctx: DialogueContext(script=[
        ("BINGO", "Nooo, I'm just a little guy"),
      ]),
      *args,
      **kwargs
    )
    bug.time = 0

  def update(bug):
    super().update()
    bug.time += 1

  def view(bug, anims=[]):
    if bug.facing[0]:
      frames = assets.sprites["bug_right"]
    elif bug.facing == (0, -1):
      frames = assets.sprites["bug_up"]
    elif bug.facing == (0, 1):
      frames = assets.sprites["bug_down"]
    move_anim = next((a for a in anims if type(a) is MoveAnim), None)
    anim_period = 4 if move_anim else 8
    return super().view(sprites=[
      Sprite(
        image=frames[bug.time // anim_period % 2],
        pos=(0, -8)
      )
    ])
