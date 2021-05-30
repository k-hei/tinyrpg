from dungeon.props import Prop
from assets import load as use_assets
from sprite import Sprite

class BagAnim:
  jump = 2
  gravity = 0.1
  bounce = 0.5
  bounces_max = 2

  def __init__(anim):
    anim.y = 0
    anim.velocity = -anim.jump
    anim.bounces = 0
    anim.done = False

  def update(anim):
    anim.y += anim.velocity
    anim.velocity += anim.gravity
    if anim.y >= 0:
      anim.y = 0
      anim.bounces += 1
      if anim.bounces >= anim.bounces_max:
        anim.velocity = 0
        anim.done = True
      else:
        anim.velocity *= -anim.bounce

class Bag(Prop):
  def __init__(bag, item):
    super().__init__(solid=False)
    bag.item = item
    bag.anim = BagAnim()

  def render(bag, anims):
    sprites = use_assets().sprites
    bag_image = sprites["bag" if bag.anim.bounces else "bag_float"]
    bag.anim.update()
    return Sprite(
      image=bag_image,
      pos=(0, bag.anim.y),
      offset=-1,
      layer="elems"
    )
