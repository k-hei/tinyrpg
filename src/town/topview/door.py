from town.topview.element import Element
from sprite import Sprite
from assets import load as use_assets
from anims.pause import PauseAnim
from lib.filters import replace_color
from colors.palette import WHITE, BLACK

class Door(Element):
  EFFECT_DELAY = 20
  OPEN_DELAY = 20
  PALETTE = (BLACK, WHITE)
  spawn_offset = (8, 8)
  rect_offset = (-16, -16)

  def __init__(door, palette=None):
    super().__init__()
    door.opened = False
    door.effect_delay = Door.EFFECT_DELAY
    door.palette = palette or Door.PALETTE

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
      hero, *_ = ctx.party
      hero.stop_move()
    return True

  def open(door):
    door.opened = True
    door.solid = False

  def view(door):
    assets = use_assets().sprites
    door_image = door.opened and assets["door_open"] or assets["door"]
    if door.palette[0] != Door.PALETTE[0]:
      door_image = replace_color(door_image, Door.PALETTE[0], door.palette[0])
    if door.palette[1] != Door.PALETTE[1]:
      door_image = replace_color(door_image, Door.PALETTE[1], door.palette[1])
    return [Sprite(
      image=door_image,
      pos=door.pos,
      origin=("center", "center"),
      layer="bg"
    )]
