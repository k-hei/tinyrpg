class Chest:
  def __init__(chest, contents):
    chest.contents = contents
    chest.opened = False
    chest.cell = None
    chest.facing = (1, 0)
    chest.faction = None
    chest.asleep = False

  def open(chest):
    contents = chest.contents
    chest.contents = None
    chest.opened = True
    return contents
