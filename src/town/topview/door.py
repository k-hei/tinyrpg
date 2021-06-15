from town.topview.element import Element
from sprite import Sprite
from assets import load as use_assets
from anims.pause import PauseAnim
from filters import replace_color
from palette import WHITE, BLUE_DARK

class Door(Element):
  EFFECT_DELAY = 20
  OPEN_DELAY = 20
  spawn_offset = (8, 8)
  rect_offset = (-16, -16)

  def __init__(door):
    super().__init__()
    door.opened = False
    door.effect_delay = Door.EFFECT_DELAY

  def reset_effect(door):
    if not door.opened:
      door.effect_delay = Door.EFFECT_DELAY

  def effect(door, ctx):
    if door.opened:
      return False
    door.effect_delay -= 1
    if not door.effect_delay:
      door.open()
      ctx.anims.append(PauseAnim(duration=Door.OPEN_DELAY))
      ctx.hero.stop_move()
    return True

  def open(door):
    door.opened = True
    door.solid = False

  def view(door, sprites):
    assets = use_assets().sprites
    door_image = door.opened and assets["door_open"] or assets["door"]
    door_image = replace_color(door_image, WHITE, BLUE_DARK)
    sprites.append(Sprite(
      image=door_image,
      pos=door.pos,
      origin=("center", "center"),
      layer="bg"
    ))
