from dungeon.element import DungeonElement

class Prop(DungeonElement):
  def __init__(prop, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def effect(prop, game):
    pass
