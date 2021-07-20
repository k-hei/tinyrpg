from dungeon.props import Prop
from assets import load as use_assets
from filters import replace_color
from anims.chest import ChestAnim
from colors.palette import PINK, GOLD, BLACK
from sprite import Sprite
from inventory import Inventory
from items import Item
from skills.weapon import Weapon

class Chest(Prop):
  def __init__(chest, contents=None, opened=False, rare=False):
    super().__init__()
    chest.contents = contents
    chest.opened = opened
    chest.rare = rare

  def encode(chest):
    [cell, kind, *props] = super().encode()
    return [cell, kind, {
      **(props[0] if props else {}),
      **(chest.contents and { "contents": chest.contents.__name__ } or {}),
      **(chest.opened and { "opened": True } or {}),
      **(chest.rare and { "rare": True } or {}),
    }]

  def open(chest):
    contents = chest.contents
    chest.contents = None
    chest.opened = True
    return contents

  def effect(chest, game):
    item = chest.contents
    if item:
      if not game.parent.inventory.is_full(Inventory.tab(item)):
        game.anims.append([
          ChestAnim(
            duration=30,
            target=chest,
            item=item(),
            on_end=chest.open
          )
        ])
        game.log.print("You open the lamp")
        if not isinstance(item, Item) and issubclass(item, Weapon):
          game.learn_skill(item)
        else:
          game.parent.inventory.append(item)
        game.log.print(("Obtained ", item().token(), "."))
        acted = True
      else:
        game.log.print("Your inventory is already full!")
    else:
      game.log.print("There's nothing left to take...")
    return True

  def view(chest, anims):
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is chest] if anims else []
    for anim in anim_group:
      if type(anim) is ChestAnim:
        frame = anim.frame + 1
        sprite = sprites["chest_open" + str(frame)]
        break
    else:
      if chest.opened:
        sprite = sprites["chest_open"]
      else:
        sprite = sprites["chest"]
    color = PINK if chest.rare else GOLD
    sprite = replace_color(sprite, BLACK, color)
    return super().view(sprite, anims)
