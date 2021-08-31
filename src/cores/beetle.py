from pygame.transform import flip
from cores import Core, Stats
import assets
from sprite import Sprite
from contexts.dialogue import DialogueContext
from anims.move import MoveAnim
from colors.palette import GREEN

class Beetle(Core):
  def __init__(beetle, name="Buge", faction="enemy", *args, **kwargs):
    super().__init__(
      name=name,
      faction=faction,
      stats=Stats(ag=6),
      color=GREEN,
      message=lambda ctx: DialogueContext(script=[
        ("Buge", "Nooo, I'm just a little guy"),
      ]),
      *args,
      **kwargs
    )
    beetle.time = 0

  def update(beetle):
    super().update()
    beetle.time += 1

  def view(beetle, anims=[]):
    if beetle.facing[0]:
      frames = assets.sprites["beetle_right"]
    elif beetle.facing == (0, -1):
      frames = assets.sprites["beetle_up"]
    elif beetle.facing == (0, 1):
      frames = assets.sprites["beetle_down"]
    move_anim = next((a for a in anims if type(a) is MoveAnim), None)
    anim_period = 4 if move_anim else 8
    return super().view(sprites=[
      Sprite(
        image=frames[beetle.time // anim_period % 2],
        pos=(0, -8)
      )
    ])
