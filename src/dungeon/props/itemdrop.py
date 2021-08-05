from dungeon.props import Prop
from sprite import Sprite

class ItemDrop(Prop):
  def __init__(drop, contents):
    drop.item = contents

  def effect(drop, game):
    game.obtain(
      item=drop.item,
      target=drop,
      on_end=lambda: game.floor.remove_elem(drop)
    )

  def view(drop, *args, **kwargs):
    return super().view([Sprite(
      image=drop.item().render(),
      pos=(0, -8)
    )], *args, **kwargs)
