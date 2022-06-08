from dungeon.props import Prop
from assets import load as use_assets
from lib.sprite import Sprite
from anims.flicker import FlickerAnim
from skills import Skill
from contexts.dialogue import DialogueContext
from helpers.combat import animate_snap


class Bag(Prop):
  def __init__(bag, contents):
    super().__init__(solid=False)
    bag.contents = contents
    bag.anim = BagAnim()

  def encode(bag):
    [cell, kind, *props] = super().encode()
    return [cell, kind, {
      **(props[0] if props else {}),
      "contents": bag.contents.__name__
    }]

  def effect(bag, game, actor):
    hero = game.hero
    if not hero:
      return False

    if actor != hero:
      return False

    def pickup_contents():
      if bag.contents:
        if game.store.obtain(bag.contents):
          item = bag.contents() if callable(bag.contents) else bag.contents
          hero.facing = (0, 1)
          game.get_tail().open(child=DialogueContext(
            lite=True,
            script=[("", ("You open the bag\n", "Received ", item.token(), "."))]
          ))
          game.anims.append([FlickerAnim(
            duration=30,
            target=bag,
            on_end=lambda: game.stage.remove_elem(bag)
          )])
        else:
          game.log.print("You can't carry any more materials...")

    animate_snap(hero, game.anims, on_end=pickup_contents)
    return True

  def view(bag, anims):
    sprites = use_assets().sprites
    bag_image = sprites["bag" if bag.anim.bounces else "bag_float"]
    bag.anim.update()
    if anims:
      bag_anim = next((a for a in anims[0] if a.target is bag), None)
      if bag_anim and type(bag_anim) is FlickerAnim and bag_anim.time % 2:
        return []
    return super().view([Sprite(
      image=bag_image,
      pos=(0, bag.anim.y),
      offset=1,
      layer="elems"
    )], anims)

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
